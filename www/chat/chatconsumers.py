import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from django.core import serializers
from .models import Connected_Users

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
                await self.send_message_gruop('GET_CONNECTED_USERS')

    #When the connection is closed              
    async def disconnect(self, close_code):
        await self.unregisterUser()
        await self.send_message_gruop('GET_CONNECTED_USERS')
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
	#send message to the group
    async def send_message_gruop(self, message):
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'group.message',
				'message': message,
			}
		)
    #Receive message from the group
    async def group_message(self, event):
        data = event['message']
        if 'GET_CONNECTED_USERS' in data:
            await self.sendConnectedUserList()

	#When receive a message
    async def receive_json(self, data):
        print(data)
        #check the command
        if 'GET_USER_LIST' in data:
            await self.sendUserList()
        elif 'GET_USERNAME' in data:
            await self.SendUsername()
        elif 'GET_CONNECTED_USERS' in data:
            await self.sendConnectedUserList()

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

    #Resgister user
    @database_sync_to_async
    def registerUser(self):
        self.unregisterUser()
        tmp = Connected_Users()
        tmp.email = self.user.email
        tmp.displayname = self.user.displayname
        tmp.save()
    
    #Unregister user
    @database_sync_to_async
    def unregisterUser(self):
        try:
            tmp = Connected_Users.objects.get(email=str(self.user.email))
            tmp.delete()
        except:
            pass

        
        
        
        
        
            

        