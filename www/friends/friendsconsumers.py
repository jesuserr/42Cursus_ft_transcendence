import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from  main.token import *
from .models import Friends_Connected_Users, Friends_List
from django.core import serializers

class FriendsConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]
        self.room_group_name = f"friends"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        #Check user is logged
        if 'tokenid' in self.scope['cookies'].keys():
            await self.getUsernameModel()
            if bool(self.user):
                await self.accept()
                await self.registerUser()
                await self.request_group_refresh_user_list('REFRESH_USER_LIST')

    #When the connection is closed              
    async def disconnect(self, close_code):
        await self.unregisterUser()
        await self.request_group_refresh_user_list('REFRESH_USER_LIST')
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
	#When receive a message
    async def receive_json(self, data):
        #check the command
        if 'GET_USER_LIST' in data:
            await self.sendUserList()
        elif 'GET_CONNECTED_USERS' in data:
            await self.sendConnectedUserList()
        elif 'FRIEND_USER' in data:
            await self.FriendsUser(data['FRIEND_USER'])
        elif 'UNFRIENDS_USER' in data:
            await self.unFriendsUser(data['UNFRIENDS_USER'])
        elif 'GET_FRIENDS_USERS' in data:
            await self.sendFriendsUserList()
           
	#Send the connected user list to the client
    async def sendConnectedUserList(self):
        data = await self.getConnectedUserList()
        await self.send_json(data)
    
	#Get list of connected users
    @database_sync_to_async
    def getConnectedUserList(self):
        friend_emails = Friends_List.objects.filter(user=self.user).values_list('email', flat=True)
        data = serializers.serialize('json', Friends_Connected_Users.objects.filter(email__in=friend_emails), fields=('displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_CONNECTED_USERS': data_obj,}
        return new_obj

	#send message to the group
    async def request_group_refresh_user_list(self, message):
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'refresh.UserList',
				'message': message,
			}
		)
    
	#Receive message from the group to refresh the user list
    async def refresh_UserList(self, event = None):
        await self.sendUserList()
        await self.sendConnectedUserList()
        await self.sendFriendsUserList()
  
  	#Send the user list to the client
    async def sendUserList(self):
        data = await self.getUserList()
        await self.send_json(data)        
    
    #Get the user list from model
    @database_sync_to_async
    def getUserList(self):
        data = serializers.serialize('json', User.objects.filter(is_superuser=False).exclude(id=self.user.id), fields=('email', 'displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_USER_LIST': data_obj,}
        return new_obj
	
	#Get the user from model
    @database_sync_to_async
    def getUsernameModel(self):
        try:
            token = self.scope['cookies']['tokenid']
            self.user = get_user_from_token(token)
        except:
            self.user = ""
            
	    #Resgister user
    @database_sync_to_async
    def registerUser(self):
        self.unregisterUser()
        tmp = Friends_Connected_Users()
        tmp.email = self.user.email
        tmp.displayname = self.user.displayname
        tmp.save()
        
    
    #Unregister user
    @database_sync_to_async
    def unregisterUser(self):
        try:
            Friends_Connected_Users.objects.get(email=str(self.user.email)).delete()
        except:
            pass

	#Send the block user list to the client
    async def sendFriendsUserList(self):
        data = await self.getFriendsUserList()
        await self.send_json(data)
    
	#Get the block user list from model
    @database_sync_to_async
    def getFriendsUserList(self):
        data = serializers.serialize('json', Friends_List.objects.filter(user=self.user), fields=('displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_FRIENDS_USERS': data_obj,}
        return new_obj
    
	#Unblock user
    async def unFriendsUser(self, data):
        await self.unFriendsUserModel(data)
        await self.refresh_UserList()
    
	#Unblock user from model
    @database_sync_to_async
    def unFriendsUserModel(self, data):
        try:
            Friends_List.objects.get(user=self.user, email=data).delete()
        except:
            pass

    #Block user
    async def FriendsUser(self, data):
        await self.FriendsUserModel(data)
        await self.refresh_UserList()
    
	#Block user from model
    @database_sync_to_async
    def FriendsUserModel(self, data):
        try:
            tmp = Friends_List.objects.get(user=self.user, email=data['email'])
        except:
            btmp = User.objects.get(email=data)
            tmp = Friends_List(user=self.user, email=btmp.email, displayname=btmp.displayname)
            tmp.save()