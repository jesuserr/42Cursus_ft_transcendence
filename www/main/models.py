from django.conf import settings
from django.db import models
from django.utils import timezone


class User(models.Model):
    email = models.EmailField(verbose_name = "Email", help_text = "Your email", primary_key=True)
    password = models.CharField(max_length=50, verbose_name = "Password")
    displayname = models.CharField(max_length=20, verbose_name = "Display Name")
    avatar = models.ImageField(verbose_name= "Avatar", blank=True)
    
    
