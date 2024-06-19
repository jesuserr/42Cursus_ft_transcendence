import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from  main.token import *
from django.core import serializers
from .models import Tournament_Connected_Users, Tournament_List, Tournament_Play

class TournamentConsumer(AsyncJsonWebsocketConsumer):
    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["tournament_name"]
        self.room_group_name = f"tournament_{self.room_name}"
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
        if 'PLAY' in data:
            await self.Play()
		
		
		
		#a apartir de aqui solo se ejecuta si el usuario es el primero conectado
        #tmpuser = await self.getFirstConnectedUser()
        #if (tmpuser.email != self.user.email):
        #    return
        
	#Get the first connected user
    @database_sync_to_async
    def getFirstConnectedUser(self):
        user = Tournament_Connected_Users.objects.filter(tournament_name=self.tournament).first()
        return user


	#Play command	
    @database_sync_to_async
    def Play(self):
        Tournament_Play.objects.filter(tournament_name=self.tournament).delete()
        users = Tournament_Connected_Users.objects.filter(tournament_name=self.tournament)
        random_users = users.order_by('?')
        for user in random_users:
            tmpuser = Tournament_Play()
            tmpuser.tournament_name = self.tournament
            tmpuser.email = user.email
            tmpuser.display_name = user.display_name
            tmpuser.status = "WAITING"
            tmpuser.save()
            print(tmpuser)
            
	#send message to the group
    async def request_group_refresh_user_list(self, message):
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'refresh.ConnectedUserList',
				'message': message,
			}
		)
        
	#Receive message from the group to refresh the user list
    async def refresh_ConnectedUserList(self, event):
        await self.sendConnectedUserList()
        
	  	#Send the user list to the client
    async def sendConnectedUserList(self):
        data = await self.getConnectedUserList()
        await self.send_json(data)        
    
    #Get the user list from model
    @database_sync_to_async
    def getConnectedUserList(self):
        data = serializers.serialize('json', Tournament_Connected_Users.objects.filter(tournament_name=self.tournament), fields=('email', 'display_name'))
        data_obj = json.loads(data)
        new_obj = {'SET_CONNECTED_USER_LIST': data_obj,}
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
        try:
            self.tournament = Tournament_List.objects.get(tournament=self.room_name)
            self.tournamentplay = Tournament_List.objects.get(tournament=self.room_name + "_PLAY")
        except:
            tmptournament = Tournament_List()
            tmptournament.tournament = self.room_name
            tmptournament.save()
            self.tournament = Tournament_List.objects.get(tournament=self.room_name)
        try:
            Tournament_Connected_Users.objects.get(tournament_name=self.tournament, email=self.user.email).delete()
        except:
            pass
        tmpuser = Tournament_Connected_Users()
        tmpuser.tournament_name = self.tournament
        tmpuser.email = self.user.email
        tmpuser.display_name = self.user.displayname
        tmpuser.save()
        
	#Unregister user
    @database_sync_to_async
    def unregisterUser(self):
        try:
            tmp = Tournament_Connected_Users.objects.get(tournament_name=self.tournament, email=self.user.email)
            tmp.delete()
        except:
            pass
        if Tournament_Connected_Users.objects.filter(tournament_name=self.tournament).exists() == False:
             self.tournament.delete()
        