from django.conf import settings
from django.db import models

class Connected_Users(models.Model):
    email = models.EmailField(verbose_name = "Email", primary_key=True)
    displayname = models.CharField(max_length=50, unique=True)