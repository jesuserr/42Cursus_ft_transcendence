from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name = "Email", primary_key=True)
    password = models.CharField(max_length=500, verbose_name = "Password")
    displayname = models.CharField(max_length=50, verbose_name = "Display Name", unique=True)
    avatar = models.ImageField(verbose_name= "Avatar", blank=True, upload_to = 'static/avatars/',)
    sessionid = models.CharField(max_length=500, blank=True)
    fourtytwo = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    objects = UserManager()  
        
class SecurityCode(models.Model):
    email = models.EmailField(primary_key=True)
    code = models.CharField(max_length=10)

    
  

