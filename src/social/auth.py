"""
What you are looking at is a bad idea. It's an authentication module that does not try to integrate itself with Django/use the Backend's
To do this decently, check this doc: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#extending-the-existing-user-model
But don't do this, It's hackish, and ugly
"""
from .models import User
import hashlib


def authenticate_user(request):
    """
    This is a warped clone of an authenticate as defined in the 
    """
    username=request.POST.get('username')
    password=hashlib.sha1(request.POST.get('password').encode()).hexdigest()
    try:
        # +++ VULNERABLE TO SQL INJECTION +++
        q = list(User.objects.raw("SELECT * FROM social_user WHERE username='{}' AND password='{}' LIMIT 1".format(username,password)))
        return q[0]
        # if len(q) > 0:
            # request.session['social_user'] = q[0].id
            # print(vars(request))
        # TODO Get last page accessed
        # return HttpResponseRedirect(reverse('social:index'))
    #Generic exception = bad practice!
    except Exception as e:
        print(e)
        return None

def get_user(user_id):
    """
    Just 
    """
    try:
        return User.objects.get(pk=user_id)
    except:
        return None