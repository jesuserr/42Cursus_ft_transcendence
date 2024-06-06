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
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.unregisterUser()
        await self.request_group_refresh_user_list('REFRESH_USER_LIST')
        
	#When receive a message
    async def receive_json(self, data):
        #check the command
        if 'GET_USER_LIST' in data:
            await self.sendUserList()
        elif 'GET_USERNAME' in data:
            await self.SendUsername()
        elif 'GET_CONNECTED_USERS' in data:
            await self.sendConnectedUserList()
        elif 'BLOCK_USER' in data:
            await self.blockUser(data['BLOCK_USER'])
        elif 'UNBLOCK_USER' in data:
            await self.unblockUser(data['UNBLOCK_USER'])
        elif 'GET_BLOCKED_USERS' in data:
            await self.sendBlockUserList()
        elif 'SEND_MESSAGE_ROOM' in data:
            await self.sendMessageRoom(data['SEND_MESSAGE_ROOM'])
        elif 'SEND_PRIVATE_MSG' in data:
            await self.sendPrivateMessage(data)
        elif 'GET_CHAT_HISTORY' in data:
            await self.getChatHistory(data)
        elif 'TYPING' in data:
            await self.typing(data)
            
	#Send the connected user list to the client
    async def sendConnectedUserList(self):
        data = await self.getConnectedUserList()
        await self.send_json(data)
    
	#Get list of connected users
    @database_sync_to_async
    def getConnectedUserList(self):
        friend_emails = Friends_List.objects.values_list('email', flat=True)
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
    async def refresh_UserList(self, event):
        await self.sendUserList()
        await self.sendConnectedUserList()
  
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
