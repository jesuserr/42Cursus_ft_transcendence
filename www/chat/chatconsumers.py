import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from django.core import serializers


class ChatConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]
        self.room_group_name = f"chat"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        #Check user is logged
        if 'sessionid' in self.scope['cookies'].keys():
            await self.getUser()
            if bool(self.user):
                await self.accept()
                #send to client some information
                await self.send_json({"User": str(self.user.displayname)})
                await self.sendUserList()

    #When the connection is closed              
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    #When receive a message
    async def receive_json(self, data):
        #check the command
        if 'list_users' in data:
            await self.sendUserList()
        elif 'chat_selected_user' in data:
            print(self.user.displayname + ":" + data)
    
        #text_data_json = json.loads(text_data)
        #message = text_data_json["message"]
        #await self.channel_layer.group_send(
        #    self.room_group_name, {"type": "chat.message", "message": self.user.email}
        #)
    #When receive a message from the group
    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
    
    #Send the user list to the client
    async def sendUserList(self):
        data = await self.getUserList()
        await self.send_json(data)        
    
    #Get the user list
    @database_sync_to_async
    def getUserList(self):
        data = serializers.serialize('json', User.objects.all(), fields=('displayname'))
        data_obj = json.loads(data)
        new_obj = {'list_users': data_obj,}
        return new_obj
    
    #Get the user
    @database_sync_to_async
    def getUser(self):
        try:
            self.user = User.objects.get(sessionid=self.scope['cookies']['sessionid'])
        except:
            self.user = ""
    
         
        
        
        
        
        
            

        