import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from django.core import serializers
from .models import Connected_Users, ChatRooms, Blocked_Users

class ChatConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]
        self.room_group_name = f"chat"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        #Check user is logged
        if 'sessionid' in self.scope['cookies'].keys():
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
        
	#send message to the group
    async def request_group_refresh_user_list(self, message):
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'refresh.UserList',
				'message': message,
			}
		)
    #Receive message from the group
    async def refresh_UserList(self, event):
            await self.sendConnectedUserList()
            await self.sendUserList()

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
            
	#Send the block user list to the client
    async def sendBlockUserList(self):
        data = await self.getBlockUserList()
        await self.send_json(data)
    
	#Get the block user list from model
    @database_sync_to_async
    def getBlockUserList(self):
        data = serializers.serialize('json', Blocked_Users.objects.filter(user=self.user, room_name=self.ChatRoom), fields=('displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_BLOCKED_USERS': data_obj,}
        return new_obj
    
	#Unblock user
    async def unblockUser(self, data):
        await self.unblockUserModel(data)
        await self.sendBlockUserList()
    
	#Unblock user from model
    @database_sync_to_async
    def unblockUserModel(self, data):
        try:
            Blocked_Users.objects.get(user=self.user, room_name=self.ChatRoom, email=data).delete()
        except:
            pass

    #Block user
    async def blockUser(self, data):
        await self.blockUserModel(data)
        await self.sendBlockUserList()
    
	#Block user from model
    @database_sync_to_async
    def blockUserModel(self, data):
        try:
            tmp = Blocked_Users.objects.get(user=self.user, room_name=self.ChatRoom, email=data['email'])
        except:
            btmp = User.objects.get(email=data)
            tmp = Blocked_Users(user=self.user, room_name=self.ChatRoom, email=btmp.email, displayname=btmp.displayname)
            tmp.save()

	#Get list of connected users
    @database_sync_to_async
    def getConnectedUserList(self):
        data = serializers.serialize('json', Connected_Users.objects.all(), fields=('displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_CONNECTED_USERS': data_obj,}
        return new_obj

    #Send the connected user list to the client
    async def sendConnectedUserList(self):
        data = await self.getConnectedUserList()
        await self.send_json(data)
    
    #Send the user list to the client
    async def sendUserList(self):
        data = await self.getUserList()
        await self.send_json(data)        
    
    #Get the user list from model
    @database_sync_to_async
    def getUserList(self):
        data = serializers.serialize('json', User.objects.all(), fields=('displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_USER_LIST': data_obj,}
        return new_obj
    
    async def SendUsername(self):
        await self.send_json({"SET_USERNAME": str(self.user.displayname), 'USER_ID': str(self.user.email)})
	
	#Get the user from model
    @database_sync_to_async
    def getUsernameModel(self):
        try:
            self.user = User.objects.get(sessionid=self.scope['cookies']['sessionid'])
        except:
            self.user = ""
        try:
            self.ChatRoom = ChatRooms.objects.get(room_name=self.room_group_name)
        except:
            self.ChatRoom = ChatRooms(room_name=self.room_group_name).save()
           
    #Resgister user
    @database_sync_to_async
    def registerUser(self):
        self.unregisterUser()
        tmp = Connected_Users(room_name=self.ChatRoom)
        tmp.email = self.user.email
        tmp.displayname = self.user.displayname
        tmp.save()
    
    #Unregister user
    @database_sync_to_async
    def unregisterUser(self):
        try:
            Connected_Users.objects.get(room_name=self.ChatRoom, email=str(self.user.email)).delete()
        except:
            pass

        
        
        
        
        
            

        