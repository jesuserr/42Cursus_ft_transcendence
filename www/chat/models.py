from django.conf import settings
from django.db import models
from main.models import User

class ChatRooms(models.Model):
	room_name = models.CharField(max_length=50, primary_key=True)
	
class Connected_Users(models.Model):
    room_name = models.ForeignKey(ChatRooms, on_delete=models.CASCADE)
    email = models.EmailField(primary_key=True)
    displayname = models.CharField(max_length=50, unique=True)
    
class Blocked_Users(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	room_name = models.ForeignKey(ChatRooms, on_delete=models.CASCADE)
	email = models.EmailField(primary_key=True)
	displayname = models.CharField(max_length=50, unique=True)

class Messages(models.Model):
	room_name = models.ForeignKey(ChatRooms, on_delete=models.CASCADE)
	email = models.EmailField()
	displayname = models.CharField(max_length=50)
	message = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

class PrivateRooms(models.Model):
	room_name = models.ForeignKey(ChatRooms, on_delete=models.CASCADE)
	private_room_name = models.CharField(max_length=200, primary_key=True)

class PrivateMessages(models.Model):
	room_name = models.ForeignKey(ChatRooms, on_delete=models.CASCADE)
	private_room_name = models.ForeignKey(PrivateRooms, on_delete=models.CASCADE)
	emailto = models.EmailField()
	displaynameto = models.CharField(max_length=50)
	emailfrom = models.EmailField()
	displaynamefrom = models.CharField(max_length=50)
	message = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)