import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import User
from channels.db import database_sync_to_async
from  main.token import *
from django.core import serializers
from .models import Tournament_Connected_Users, Tournament_List, Tournament_Play

class TournamentConsumer(AsyncJsonWebsocketConsumer):
    tournament_dict = {}

    #When the connection is established
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["tournament_name"]
        self.room_group_name = f"tournament_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        TournamentConsumer.tournament_dict.setdefault(self.room_group_name, {})
        TournamentConsumer.tournament_dict[self.room_group_name].setdefault('text', 'Waiting for players')
        TournamentConsumer.tournament_dict[self.room_group_name].setdefault('status', 1)
        #Check user is logged
        if 'tokenid' in self.scope['cookies'].keys():
            await self.getUsernameModel()
            if bool(self.user):
                await self.accept()
                await self.registerUser()
                await self.request_group_refresh_user_list('REFRESH_USER_LIST')
                connected_users_count = await self.get_connected_users_count()
                if TournamentConsumer.tournament_dict[self.room_group_name]['text'] == 'Waiting for players' and connected_users_count > 2:
                     TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Start the tournament'
                     TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 0
                elif TournamentConsumer.tournament_dict[self.room_group_name]['text'] == 'Start the tournament' and connected_users_count < 3:
                     TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Waiting for players'
                     TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 1
                msg = {'SET_BUTTON_PLAY_STATUS': {'text': TournamentConsumer.tournament_dict[self.room_group_name]['text'], 'status': TournamentConsumer.tournament_dict[self.room_group_name]['status']}}
                await self.send_group_msg(msg)

    #When the connection is closed              
    async def disconnect(self, close_code):
        await self.unregisterUser()
        await self.request_group_refresh_user_list('REFRESH_USER_LIST')
        if TournamentConsumer.tournament_dict[self.room_group_name]['text'] == 'Tournament started':
            data = await self.PlayModel()
            await self.request_group_refresh_tournament_status(data)
        connected_users_count = await self.get_connected_users_count()
        if TournamentConsumer.tournament_dict[self.room_group_name]['text'] == 'Waiting for players' and connected_users_count > 2:
            TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Start the tournament'
            TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 0
        elif TournamentConsumer.tournament_dict[self.room_group_name]['text'] == 'Start the tournament' and connected_users_count < 3:
            TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Waiting for players'
            TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 1
        msg = {'SET_BUTTON_PLAY_STATUS': {'text': TournamentConsumer.tournament_dict[self.room_group_name]['text'], 'status': TournamentConsumer.tournament_dict[self.room_group_name]['status']}}
        await self.send_group_msg(msg)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
	#When receive a message
    async def receive_json(self, data):
        if 'PLAY' in data:
            TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Tournament started'
            TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 1
            msg = {'SET_BUTTON_PLAY_STATUS': {'text': TournamentConsumer.tournament_dict[self.room_group_name]['text'], 'status': TournamentConsumer.tournament_dict[self.room_group_name]['status']}}
            await self.send_group_msg(msg)
            await self.Play()
            
    #Get the connected user count
    @database_sync_to_async
    def get_connected_users_count(self):
        return Tournament_Connected_Users.objects.filter(tournament_name=self.tournament).count()
	
	#send message to the group
    async def send_group_msg(self, message):
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'refresh.ButtonPlay',
				'message': message,
			}
		)
		
	#Receive message from the group to refresh the button play
    async def refresh_ButtonPlay(self, event):
        await self.send_json(event['message'])
        
	#Get the first connected user
    @database_sync_to_async
    def CheckIsTheFirstConnectedUser(self):
        tmpuser = Tournament_Connected_Users.objects.filter(tournament_name=self.tournament).first()
        if(tmpuser.email == self.user.email):
            return True
        return False
    
    @database_sync_to_async
    def check_waiting_status(self):
        waiting_count = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WAITING').count()
        if waiting_count >= 2:
            return True
        return False
    
    @database_sync_to_async
    def delete_tournament_play_records(self):
        Tournament_Play.objects.filter(tournament_name=self.tournament).delete()
    @database_sync_to_async
    def get_game_name_msg(self):
        players = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WAITING')[:2]
        game_name = "/game5/"
        game_name += self.tournament.tournament
        for player in players:
            game_name += '_' + player.email
        msg = {'START_GAME': {'name': game_name, 'Player1': players[0].email, 'Player2': players[1].email}}
        return msg

	#Play command	
    async def Play(self):
        data = await self.PlayModelInit()
        await self.request_group_refresh_tournament_status(data)
        if await self.check_waiting_status():
            msg = await self.get_game_name_msg()
            print(msg)
        
        
    async def request_group_refresh_tournament_status(self, message):
        await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'refresh.tournament_status',
				'message': message,
			}
		)
        
	#Receive message from the group to refresh the tournament status
    async def refresh_tournament_status(self, event):
        await self.send_json(event['message'])
    
	#Get the tournament status from model
    @database_sync_to_async
    def PlayModel(self):
        data = serializers.serialize('json', Tournament_Play.objects.filter(tournament_name=self.tournament), fields=('email', 'display_name', 'status'))
        data_obj = json.loads(data)
        new_obj = {'REFRESH_TURNAMENT_STATUS': data_obj,}
        return new_obj	

    @database_sync_to_async
    def PlayModelInit(self):
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
        data = serializers.serialize('json', Tournament_Play.objects.filter(tournament_name=self.tournament), fields=('email', 'display_name', 'status'))
        data_obj = json.loads(data)
        new_obj = {'REFRESH_TURNAMENT_STATUS': data_obj,}
        return new_obj
            
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
        except:
            tmptournament = Tournament_List()
            tmptournament.tournament = self.room_name
            tmptournament.save()
            self.tournament = Tournament_List.objects.get(tournament=self.room_name)
        try:
            Tournament_Connected_Users.objects.get(tournament_name=self.tournament, email=self.user.email).delete()
        except:
            pass
        try:
            tmpuser = Tournament_Connected_Users()
            tmpuser.tournament_name = self.tournament
            tmpuser.email = self.user.email
            tmpuser.display_name = self.user.displayname
            tmpuser.save()
        except:
            pass
        
	#Unregister user
    @database_sync_to_async
    def unregisterUser(self):
        try:
            tournament_play = Tournament_Play.objects.get(tournament_name=self.tournament, email=self.user.email)
            if tournament_play.status == 'WAITING':
                tournament_play.status = 'LOST_CONNECTION'
                tournament_play.save()
        except:
        	pass
        
        try:
            tmp = Tournament_Connected_Users.objects.get(tournament_name=self.tournament, email=self.user.email)
            tmp.delete()
        except:
            pass
        if Tournament_Connected_Users.objects.filter(tournament_name=self.tournament).exists() == False:
             self.tournament.delete()
        