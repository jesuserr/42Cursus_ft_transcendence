import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pongapi.models import User
from channels.db import database_sync_to_async
from django.core import serializers
from .models import Connected_Users, ChatRooms, Blocked_Users, Messages, PrivateRooms, PrivateMessages
from  pongapi.token import *

class ChatConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
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
        elif 'SEND_MESSAGE_ROOM' in data:
            await self.sendMessageRoom(data['SEND_MESSAGE_ROOM'])
        elif 'SEND_PRIVATE_MSG' in data:
            await self.sendPrivateMessage(data)
        elif 'GET_CHAT_HISTORY' in data:
            await self.getChatHistory(data)
        elif 'TYPING' in data:
            await self.typing(data)
            
	#Send typing status to the group
    async def typing(self, data):
        data['WHO'] = self.user.displayname
        data['WHOEMAIL'] = self.user.email
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'typing.message',
				'message': json.dumps(data),
			}
		)
    
	#Send typing status to the client
    async def typing_message(self, event):
        data_obj = json.loads(event['message'])
        if (data_obj['WHOEMAIL'] != self.user.email):
            await self.send_json(data_obj)
            
	#Get chat history
    async def getChatHistory(self, data):
        await self.sendChatHistory(await self.getChatHistoryModel(data))
        
	#Get chat history from model
    @database_sync_to_async
    def getChatHistoryModel(self, data):
        if 'LENGTH' in data:
            size = data['LENGTH']
        else:
            size = 100
        if (data['GET_CHAT_HISTORY'] == ''):
            #Get the last x messages and filter the block users
            blocked_users = Blocked_Users.objects.filter(user=self.user, room_name=self.ChatRoom).values_list('email', flat=True)
            datadb = serializers.serialize('json', Messages.objects.filter(room_name=self.ChatRoom).exclude(email__in=blocked_users).order_by('-id')[:size][::-1], fields=('email', 'displayname', 'message'))
            data_obj = json.loads(datadb)
            new_obj = {'SET_CHAT_HISTORY': '', 'DATA': data_obj,}
            return new_obj
        else:
            #Get the last x messages and filter the block users
            blocked_users = Blocked_Users.objects.filter(user=self.user, room_name=self.ChatRoom).values_list('email', flat=True)
            private_room_name = sorted([self.user.email, data['GET_CHAT_HISTORY']])
            try:
                tmpprivate = PrivateRooms.objects.get(room_name=self.ChatRoom, private_room_name=private_room_name)
            except:
                tmpprivate = ''
            datadb = serializers.serialize('json', PrivateMessages.objects.filter(private_room_name=tmpprivate).exclude(emailfrom__in=blocked_users).order_by('-id')[:size][::-1], fields=('email', 'displaynameto', 'emailfromto', 'displaynamefrom', 'message'))
            data_obj = json.loads(datadb)
            new_obj = {'SET_CHAT_HISTORY': data['GET_CHAT_HISTORY'], 'DATA': data_obj,}
            return new_obj
        

	#Send chat history to the client
    async def sendChatHistory(self, data):
        await self.send_json(data)
        
	#Send private message 
    async def sendPrivateMessage(self, data):
        await self.sendPrivateMessageModel(data)
        private_room_name = sorted([self.user.email, data['SEND_PRIVATE_MSG']])
        message_data = {
        	'private_room_name': private_room_name,
        	'emailfrom': self.user.email,
        	'displaynamefrom': self.user.displayname,
            'emailto': data['SEND_PRIVATE_MSG'],
        	'displayto': data['DISPLAYNAMETO'],
        	'message': data['MESSAGE'],
		}
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'private.room.message',
				'message': json.dumps(message_data),
			}
		)
	
	#Send private message 
    async def private_room_message(self, event):
        data_obj = json.loads(event['message'])
        #Cherck if the msg is for my private room
        if ((data_obj['emailto'] == self.user.email) or data_obj['emailfrom'] == self.user.email) and not (await self.is_user_blocked(data_obj['emailfrom'])):
            new_obj = {'NEW_PRIVATE_MSG': data_obj,}
            await self.send_json(new_obj)
		
	#Send private message to room model
    @database_sync_to_async
    def sendPrivateMessageModel(self, data):
        local_private_room_name = sorted([self.user.email, data['SEND_PRIVATE_MSG']])
        try:
            tmpprivate = PrivateRooms.objects.get(room_name=self.ChatRoom, private_room_name=local_private_room_name)
        except:
            tmpprivate = PrivateRooms(room_name=self.ChatRoom, private_room_name=local_private_room_name)
            tmpprivate.save()
        tmp = PrivateMessages()
        tmp.private_room_name = tmpprivate
        tmp.emailto = data['SEND_PRIVATE_MSG']
        tmp.displaynameto = data['DISPLAYNAMETO']
        tmp.emailfrom = self.user.email
        tmp.displaynamefrom = self.user.displayname
        tmp.message = data['MESSAGE']
        tmp.save()
	
	#Send message to room
    async def sendMessageRoom(self, data):
        await self.sendMessageRoomModel(data)
        message_data = {
        	'room_name': self.room_group_name,
        	'email': self.user.email,
        	'displayname': self.user.displayname,
        	'message': data,
		}
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'chat.room.message',
				'message': json.dumps(message_data),
			}
		)
        
    
	#Check if the user is blocked in the database
    @database_sync_to_async
    def is_user_blocked(self, user_email):
        try:
            Blocked_Users.objects.get(user=self.user, room_name=self.ChatRoom, email=user_email)
            user_blocked = True
        except:
            user_blocked = False
        return user_blocked

    #Send message to room model
    @database_sync_to_async
    def sendMessageRoomModel(self, data):
        tmp = Messages(room_name=self.ChatRoom, email=self.user.email, displayname=self.user.displayname, message=data)
        tmp.save()

	#Send message to the group
    async def chat_room_message(self, event):
        data_obj = json.loads(event['message'])
        #Check if the user is blocked
        if not (await self.is_user_blocked(data_obj['email'])):
            new_obj = {'NEW_ROOM_MSG': data_obj,}
            await self.send_json(new_obj)
            
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
        print(data)
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
        data = serializers.serialize('json', Connected_Users.objects.filter(room_name=self.ChatRoom), fields=('displayname'))
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
        data = serializers.serialize('json', User.objects.filter(is_superuser=False), fields=('email', 'displayname'))
        data_obj = json.loads(data)
        new_obj = {'SET_USER_LIST': data_obj,}
        return new_obj
    
    async def SendUsername(self):
        await self.send_json({"SET_USERNAME": str(self.user.displayname), 'USER_ID': str(self.user.email)})
	
	#Get the user from model
    @database_sync_to_async
    def getUsernameModel(self):
        try:
            token = self.scope['cookies']['tokenid']
            self.user = get_user_from_token(token)
        except:
            self.user = ""
        try:
            self.ChatRoom = ChatRooms.objects.get(room_name=self.room_group_name)
        except:
            self.ChatRoom = ChatRooms(room_name=self.room_group_name)
            self.ChatRoom.save()
                       
    #Resgister user
    @database_sync_to_async
    def registerUser(self):
        self.unregisterUser()
        tmp = Connected_Users(room_name=self.ChatRoom)
        tmp.email = self.user.email
        tmp.displayname = self.user.displayname
        tmp.save()
        #get the chat room
        self.ChatRoom = ChatRooms.objects.get(room_name=self.room_group_name)        
    
    #Unregister user
    @database_sync_to_async
    def unregisterUser(self):
        try:
            Connected_Users.objects.get(room_name=self.ChatRoom, email=str(self.user.email)).delete()
        except:
            pass

        
        