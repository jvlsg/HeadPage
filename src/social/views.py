from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
#from django.template import loader
from django.conf import settings
from django.views import generic
from .models import User
from .forms import RegisterForm, LoginForm, EditProfileForm
import hashlib
import subprocess
import os
from django.db import connection
from .auth import authenticate_user, get_user

class IndexView(generic.ListView):
    template_name = 'social/index.html'
    context_object_name = 'users_alphabetical_list'

    def get_queryset(self):
        """Return the last five published questions."""
        try:
            return User.objects.order_by('username')[:5]
        except django.db.utils.OperationalError:
            return None

def user_profile(request):
    logged_user = get_user(request.session.get('user_id'))

    if request.POST:
        form = EditProfileForm(request.POST)
        if form.is_valid():
            pic_url = form.cleaned_data["profile_picture_from_url"]
            print(">>>"+pic_url)
            if len(pic_url)>0:
                # +++ VULNERABLE TO REMOTE CODE EXECUTION +++
                subprocess.run( "wget {} -O {}.jpg".format(pic_url,settings.MEDIA_ROOT+logged_user.username), shell=True)
        return HttpResponse("Welcome to your page, "+logged_user.first_name)
    
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
            form = EditProfileForm()
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
            #+++ USE OF BROKEN HASH FUNCTION SHA1 +++
            password=hashlib.sha1(request.POST.get('password').encode()).hexdigest()                    
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