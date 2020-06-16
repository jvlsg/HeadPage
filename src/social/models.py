from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=16)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    about = models.TextField(default="",null=True)
    
    def __str__(self):
        return str(self.username)
        
class File(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=300, default="")
    path = models.CharField(max_length=3000, default="")
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return "{} Owned by: {}".format(self.name,self.owner)