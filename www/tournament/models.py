from django.conf import settings
from django.db import models
from main.models import User

class Tournament_List(models.Model):
    tournament = models.CharField(max_length=50, primary_key=True)

class Tournament_Connected_Users(models.Model):
    tournamnet_name = models.ForeignKey(Tournament_List, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)