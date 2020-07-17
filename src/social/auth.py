"""
What you are looking at is a bad idea. It's an authentication module that does not try to integrate itself with Django/use the Backend's
To do this decently, check this doc: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#extending-the-existing-user-model
But don't do this, It's hackish, and ugly
"""
from .models import User
import hashlib

def get_password_hash(password):
    #+++ USE OF BROKEN HASH FUNCTION SHA1 +++
    return hashlib.sha1(password.encode()).hexdigest()

def authenticate_user(username,password):
    """
    This is a warped clone of an 'authenticate' as defined in the django docs
    """
    password=get_password_hash(password)
    try:
        # +++ VULNERABLE TO SQL INJECTION +++
        q = list(User.objects.raw("SELECT * FROM social_user WHERE username='{}' AND password='{}' LIMIT 1".format(username,password)))
        return q[0]
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