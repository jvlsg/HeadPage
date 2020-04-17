from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.template import loader
from django.views import generic
from .models import User

# # Create your views here.
class IndexView(generic.ListView):
    template_name = 'social/index.html'
    context_object_name = 'users_alphabetical_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return User.objects.order_by('username')[:5]

def user_profile(request,username):
    retrieved_user = get_object_or_404(User, username=username)
    return render(request, 'social/profile.html', {'user': retrieved_user})
