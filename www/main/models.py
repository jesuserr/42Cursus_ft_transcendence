from django.conf import settings
from django.db import models
from django.utils import timezone


class User(models.Model):
    email = models.EmailField(verbose_name = "Email", primary_key=True)
    password = models.CharField(max_length=500, verbose_name = "Password")
    displayname = models.CharField(max_length=20, verbose_name = "Display Name", unique=True)
    avatar = models.ImageField(verbose_name= "Avatar", blank=True, upload_to = 'static/avatars/',)
    sessionid = models.CharField(max_length=500, blank=True)
    
  

