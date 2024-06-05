import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from  main.token import *

class FriendsConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]
        self.room_group_name = f"friends"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print("Connected")

    #When the connection is closed              
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print("Disconnected")
        
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
  