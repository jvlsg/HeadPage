import subprocess
import os.path
from django.conf import settings

def write_file(f,path):
    with open( os.path.join(settings.MEDIA_ROOT,path) , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def move_file(old_path,new_path):
    # +++ VULNERABLE TO RCE (REMOTE CODE EXECUTION) +++
    subprocess.run( "mv {} {} ".format( os.path.join(settings.MEDIA_ROOT,old_path) , os.path.join(settings.MEDIA_ROOT,new_path) ), shell=True)

def delete_file(path):
    # +++ VULNERABLE TO RCE (REMOTE CODE EXECUTION) +++
    subprocess.run( "rm -f {} ".format(os.path.join(settings.MEDIA_ROOT,path)), shell=True)