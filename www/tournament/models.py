from django.conf import settings
from django.db import models
from main.models import User

class Tournament_List(models.Model):
    tournament = models.CharField(max_length=50, primary_key=True)
    status = models.CharField(max_length=50, default='PENDING')

class Tournament_Connected_Users(models.Model):
    tournament_name = models.ForeignKey(Tournament_List, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=50, unique=True)

class Tournament_Play(models.Model):
    tournament_name = models.ForeignKey(Tournament_List, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50)

class Tournament_Round(models.Model):
    tournament_name = models.ForeignKey(Tournament_List, on_delete=models.CASCADE)
    round_name = models.CharField(max_length=50)
    player1 = models.EmailField()
    player2 = models.EmailField()
    
    