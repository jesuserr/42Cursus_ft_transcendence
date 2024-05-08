import json
import asyncio
import functools
import time
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from django.core import serializers
import django.core.serializers
from django.forms.models import model_to_dict


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]
        self.room_group_name = f"chat"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        #Check user is logged
        if 'sessionid' in self.scope['cookies'].keys():
          await self.getUser()
          if bool(self.user):
               await self.accept()
               await self.send(text_data=json.dumps({"User": str(self.user.displayname)}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'list_users' in text_data:
              await self.sendUserList()
        elif 'chat_selected_user' in text_data:
              print(self.user.displayname + ":" + text_data)
		#text_data_json = json.loads(text_data)
        #message = text_data_json["message"]
        #await self.channel_layer.group_send(
        #    self.room_group_name, {"type": "chat.message", "message": self.user.email}
        #)
    
    async def sendUserList(self):
        data = await self.getUserList()
        print(data)
        await self.send(text_data=data)

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
        
    @database_sync_to_async
    def getUserList(self):
          print("getUserList")
          data = serializers.serialize('json', User.objects.all(), fields=('displayname'))
          data_obj = json.loads(data)
          new_obj = {'list_users': data_obj,}
          return json.dumps(new_obj)
     
    @database_sync_to_async
    def getUser(self):
    	try:
        		self.user = User.objects.get(sessionid=self.scope['cookies']['sessionid'])
    	except:
                self.user = ""
    
         
        
        
        
        
        
            

        