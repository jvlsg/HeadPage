from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.template import loader
from django.views import generic
from .models import User
from .forms import RegisterForm, LoginForm
import hashlib
from django.db import connection
from pprint import pprint
from .auth import authenticate_user, get_user
# # Create your views here.
class IndexView(generic.ListView):
    template_name = 'social/index.html'
    context_object_name = 'users_alphabetical_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return User.objects.order_by('username')[:5]

def user_profile(request,username):

    #TODO user a RAW SQL QUERY, make it vulnerable
    retrieved_user = get_object_or_404(User, username=username)
    logged_user = get_user(request.session.get('user_id'))
    if logged_user == retrieved_user:
        ##TODO Form for editing
        #Form = ...
        return HttpResponse("Welcome to your page, "+logged_user.first_name)
    return render(request, 'social/profile.html', {'user': retrieved_user})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        error_message = ""
        if form.is_valid():
            curs = connection.cursor()

            username=request.POST.get('username')
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')

            #+++ PASSWORD HASHED ON THE SERVERSIDE +++
            password=hashlib.sha1(request.POST.get('password').encode()).hexdigest()                    
            try:
                # +++ VULNERABLE TO SQL INJECTION +++
                curs.executescript(
                    "INSERT INTO social_user ('username','password','first_name','last_name') VALUES ('{}','{}','{}','{}')".format(username,password,first_name,last_name)
                )
                #TODO Redirect to Edit Profile
                return HttpResponseRedirect(reverse('social:index'))
            #Generic exception = bad practice!
            except Exception as e:
                form = RegisterForm()
                error_message="ERROR! Username already taken!\n{}".format(e)
    else:
        form = RegisterForm()
        error_message=""
    return render(request,'social/register.html',{'form': form,"error_message":error_message})

def login(request):
    if request.method=='POST':
        ## Auth and shite
        form = LoginForm(request.POST)
        error_message = ""
        if form.is_valid():
            user = authenticate_user(request)
            if user != None:
                request.session['user_id'] = user.id
                return HttpResponseRedirect(reverse('social:index'))
            form = LoginForm()
            error_message="Failure logging In!(Worng username/password?)\n"
    else:
        form = LoginForm()
        error_message=""
    return render(request,'social/login.html',{'form': form,"error_message":error_message})


def logout(request):
    request.session.pop('user_id')
    return HttpResponseRedirect(reverse('social:index'))
##TODO -Generic 'form' view with functions for auth and registering? Does Django already have these?