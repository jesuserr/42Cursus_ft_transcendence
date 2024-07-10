from django.conf import settings
from django.db import models
from pongapi.models import User

# Create your models here.
class Friends_List(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	email = models.EmailField(primary_key=True)
	displayname = models.CharField(max_length=50, unique=True)

class Friends_Connected_Users(models.Model):
    email = models.EmailField(primary_key=True)
    displayname = models.CharField(max_length=50, unique=True)