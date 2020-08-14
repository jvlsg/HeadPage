from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
#from django.template import loader
from django.conf import settings
from django.views import generic
from .models import User, File
from .forms import RegisterForm, LoginForm, EditProfileForm, FileUploadForm, FileManagementForm
import subprocess
import os
from django.db import connection
from .auth import authenticate_user, get_user, get_password_hash
from . import storage
import mimetypes

class IndexView(generic.ListView):
    template_name = 'social/index.html'
    context_object_name = 'users_alphabetical_list'

    def get_queryset(self):
        """Return the last five published questions."""
        try:
            return User.objects.order_by('username')
        except django.db.utils.OperationalError:
            return None

#God, just LOOK at this mess
def user_profile(request):
    logged_user = get_user(request.session.get('user_id'))

    if request.POST and logged_user != None:
        profile_form = EditProfileForm(request.POST,request.FILES)

        if profile_form.is_valid():
            # There are better ways to check for differences and update a model using a form
            # Check out the ModelForm() in the docs.
            pic_url = profile_form.cleaned_data["profile_picture_from_url"]
            new_password = profile_form.cleaned_data["password"]
            if len(pic_url)>0:
                # +++ VULNERABLE TO RCE (REMOTE CODE EXECUTION) +++
                subprocess.run( "wget {} -O {}{}{}.jpg".format(pic_url, settings.MEDIA_ROOT,"/avatars/",str(logged_user.id)), shell=True)
            #File uploaded in the field
            elif request.FILES.get("profile_picture_from_file",None) != None:
                # +++ VULNERABLE TO Unrestricted Upload of File with Dangerous Type +++
                storage.write_file(request.FILES["profile_picture_from_file"],"{}{}.jpg".format("/avatars/",str(logged_user.id)))
            if len(new_password) > 0:
                logged_user.password = get_password_hash(new_password)
            logged_user.first_name = profile_form.cleaned_data["first_name"]
            logged_user.last_name = profile_form.cleaned_data["last_name"]
            logged_user.about = profile_form.cleaned_data["about"]
            logged_user.save()
            
        return redirect(reverse("social:profile")+"?userid={}".format(logged_user.id))

    elif request.GET:
        try:
            #Check GET params 
            userid=request.GET.get('userid')
            #+++ VULNERABLE TO SQL INJECTION+++
            profile_user = list(User.objects.raw("SELECT  * FROM social_user WHERE id='{}'".format(userid)))[0]
            user_public_files = list(File.objects.filter(owner=userid, is_public=True))
        except:
            raise Http404("Profile does not exist")

        profile_form = None
        file_upload_form = None
        user_file_forms = []
        if logged_user == profile_user:
            profile_form = EditProfileForm(initial= {
                    "first_name":logged_user.first_name,
                    "last_name":logged_user.last_name,
                    "about":logged_user.about,})
            file_upload_form = FileUploadForm()
            user_files = list(File.objects.filter(owner=logged_user.id))

            for f in user_files:
                user_file_forms.append(FileManagementForm(instance=f))

        return render(request, 'social/profile.html', 
            {'user': profile_user,'edit_profile_form':profile_form,"file_upload_form":file_upload_form ,'user_public_files':user_public_files,'user_file_forms':user_file_forms})

def upload_file(request):
    logged_user = get_user(request.session.get('user_id'))
    if request.POST and logged_user != None:
        file_upload_form = FileUploadForm(request.POST,request.FILES)
        if file_upload_form.is_valid():
            if request.FILES.get("file_upload",None) != None:
                file_upload_name = file_upload_form.cleaned_data["file_upload_name"] or request.FILES["file_upload"].name
                file_upload_is_public = file_upload_form.cleaned_data["file_upload_is_public"]
                file_upload_path = "{}/{}/{}".format("files",logged_user.id,file_upload_name)
                # +++ VULNERABLE TO Unrestricted Upload of File with Dangerous Type +++
                storage.write_file(request.FILES["file_upload"],file_upload_path)
                f = File(name=file_upload_name,owner=logged_user,is_public=file_upload_is_public,path=file_upload_path)
                f.save()
        return redirect(reverse("social:profile")+"?userid={}".format(logged_user.id))

def edit_file(request):
    #TODO check for user login(?) , rename the file
    logged_user = get_user(request.session.get('user_id'))
    if request.POST and logged_user != None:
        file = File.objects.get(id=request.GET.get("id"))
        old_name = file.name
        old_path = file.path

        edit_form = FileManagementForm(request.POST,instance = file)
        edit_form.save()
        
        if old_name != file.name:
            file.path=file.path.replace(old_name,file.name)
            storage.move_file(old_path,file.path)

        file.save()
        return redirect(reverse("social:profile")+"?userid={}".format(logged_user.id))

def delete_file(request):
    logged_user = get_user(request.session.get('user_id'))
    if request.POST and logged_user != None:
        try:
            original_file = File.objects.get(id=request.GET.get("id"),owner=logged_user)
        except:
            #TODO don't return a 404, but a decent error message
            raise Http404("File does not exist")
        finally:
            storage.delete_file(original_file.path)
            original_file.delete()
            return redirect(reverse("social:profile")+"?userid={}".format(logged_user.id))

def static(request):
    if request.GET:
        #+++VULNERABLE TO PATH TRANSVERSAL+++
        # This is a pretty forced example, but it does demonstrate the vulnerability in itself
        path = os.path.join(settings.BASE_DIR,"social/static/social/",request.GET.get("file"))
        file = open(path,"rb")
        response = HttpResponse(file, content_type=mimetypes.guess_type(path)[0])
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(request.GET.get("file"))
        return response

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        error_message = ""
        #+++ VULNERABLE TO UNVALIDATED REDIRECTS +++
        url_to_redirect = request.session.pop("login_redirect",reverse('social:index'))
        if form.is_valid():
            curs = connection.cursor()

            username=request.POST.get('username')
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')

            #+++ PASSWORD HASHED ON THE SERVERSIDE +++
            password=get_password_hash(request.POST.get('password'))
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
        if(request.GET.get("redirect")):
            request.session["login_redirect"] = request.GET.get("redirect")
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