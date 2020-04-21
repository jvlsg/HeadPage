from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.template import loader
from django.views import generic
from .models import User
from .forms import RegisterForm, LoginForm
import hashlib
from django.db import connection
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
    return render(request, 'social/profile.html', {'user': retrieved_user})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        error_message = ""
        if form.is_valid():
            curs = connection.cursor()

            # TODO Check if username is valid ?

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
                #return HttpResponseRedirect(reverse('social:index'))
                return HttpResponse(str("Welcome! "+username))
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
            username=request.POST.get('username')
            password=hashlib.sha1(request.POST.get('password').encode()).hexdigest()
            try:
                # +++ VULNERABLE TO SQL INJECTION +++
                q = list(User.objects.raw("SELECT * FROM social_user WHERE username='{}' AND password='{}'".format(username,password)))
                if len(q) > 0:
                    request.session['user_id'] = q[0].id
                    request.user = q[0]
                    print(vars(request))
                ## TODO Get last page accessed
                return HttpResponseRedirect(reverse('social:index'))
            #Generic exception = bad practice!
            except Exception as e:
                form = LoginForm()
                error_message="ERROR!\n{}".format(e)
    else:
        form = LoginForm()
        error_message=""
    return render(request,'social/login.html',{'form': form,"error_message":error_message})

##TODO -Generic 'form' view with functions for auth and registering? Does Django already have these?