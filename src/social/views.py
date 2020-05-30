from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
#from django.template import loader
from django.conf import settings
from django.views import generic
from .models import User
from .forms import RegisterForm, LoginForm, EditProfileForm
import subprocess
import os
from django.db import connection
from .auth import authenticate_user, get_user
from .storage import write_file

class IndexView(generic.ListView):
    template_name = 'social/index.html'
    context_object_name = 'users_alphabetical_list'

    def get_queryset(self):
        """Return the last five published questions."""
        try:
            return User.objects.order_by('username')[:5]
        except django.db.utils.OperationalError:
            return None

#God, just LOOK at this mess
def user_profile(request):
    logged_user = get_user(request.session.get('user_id'))

    if request.POST and logged_user != None:
        form = EditProfileForm(request.POST,request.FILES)
        if form.is_valid():
            # There are better ways to check for differences and update a model using a form
            # Check out the ModelForm() in the docs.
            pic_url = form.cleaned_data["profile_picture_from_url"]
            new_password = form.cleaned_data["password"]
            
            if len(pic_url)>0:
                # +++ VULNERABLE TO REMOTE CODE EXECUTION +++
                subprocess.run( "wget {} -O {}.jpg".format(pic_url,settings.MEDIA_ROOT+"/avatars/"+logged_user.username), shell=True)
            
            #File uploaded in the field
            elif(request.FILES["profile_picture_from_file"]):
                # +++ VULNERABLE TO Unrestricted Upload of File with Dangerous Type +++
                write_file(request.FILES["profile_picture_from_file"],'{}.jpg'.format(settings.MEDIA_ROOT+"/avatars/"+logged_user.username))

            if len(new_password) > 0:
                logged_user.password = auth.get_password_hash(new_password)
            
            logged_user.first_name = form.cleaned_data["first_name"]
            logged_user.last_name = form.cleaned_data["last_name"]
            logged_user.about = form.cleaned_data["about"]
            logged_user.save()
            return redirect(reverse("social:profile")+"?username={}".format(logged_user.username))
        return redirect(reverse("social:index"))

    elif request.GET:
        try:
            #Check GET params 
            username=request.GET.get('username')
            #+++ VULNERABLE TO SQL INJECTION+++
            profile_user = list(User.objects.raw("SELECT  * FROM social_user WHERE username='{}'".format(username)))[0]
        except:
            raise Http404("Profile does not exist")

        form = None
        if logged_user == profile_user:
            form = EditProfileForm(initial= {
                    "first_name":logged_user.first_name,
                    "last_name":logged_user.last_name,
                    "about":logged_user.about,})
            #TODO list user uploaded files
        return render(request, 'social/profile.html', {'user': profile_user,'edit_profile_form':form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        error_message = ""
        url_to_redirect = request.POST.get("redirect")
        if form.is_valid():
            curs = connection.cursor()

            username=request.POST.get('username')
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')

            #+++ PASSWORD HASHED ON THE SERVERSIDE +++
            password=auth.get_password_hash(request.POST.get('password'))
            try:
                # +++ VULNERABLE TO SQL INJECTION +++
                curs.executescript(
                    "INSERT INTO social_user ('username','password','first_name','last_name') VALUES ('{}','{}','{}','{}')".format(
                        username,password,first_name,last_name)
                )
                #+++ VULNERABLE TO UNVALIDATED REDIRECTS +++
                return redirect(url_to_redirect)
            #--- Generic exception = bad practice! ---
            except Exception as e:
                form = RegisterForm()
                error_message="ERROR! Username already taken!\n{}".format(e)
    else:
        form = RegisterForm()
        error_message=""
    return render(request,'social/register.html',{'form': form,"error_message":error_message})

def login(request):
    if request.method=='POST':
        #+++ VULNERABLE TO UNVALIDATED REDIRECTS +++
        url_to_redirect = request.session.pop("login_redirect",reverse('social:index'))
        form = LoginForm(request.POST)
        error_message = ""
        if form.is_valid():
            user = authenticate_user(form.cleaned_data["username"],form.cleaned_data["password"])
            if user != None:
                request.session['user_id'] = user.id
                return redirect(url_to_redirect)
            form = LoginForm()
            error_message="Failure logging In!(Worng username/password?)\n"
    else:
        if(request.GET.get("redirect")):
            request.session["login_redirect"] = request.GET.get("redirect")
        form = LoginForm()
        error_message=""
    return render(request,'social/login.html',{'form': form,"error_message":error_message})


def logout(request):
    request.session.pop('user_id')
    #+++ VULNERABLE TO UNVALIDATED REDIRECTS +++
    url_to_redirect = request.GET.get("redirect",reverse('social:index'))
    return redirect(url_to_redirect)