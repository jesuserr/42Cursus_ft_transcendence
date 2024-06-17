import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from  main.token import *
from django.core import serializers

class TournamentConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["tournament_name"]
        self.room_group_name = f"tournament_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        #Check user is logged
        await self.accept()

    #When the connection is closed              
    async def disconnect(self, close_code):
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
           
	