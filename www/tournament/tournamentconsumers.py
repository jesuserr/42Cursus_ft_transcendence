import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pongapi.models import User
from channels.db import database_sync_to_async
from  pongapi.token import *
from django.core import serializers
from .models import Tournament_Connected_Users, Tournament_List, Tournament_Play, Tournament_Round
import time
import asyncio


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
                await self.request_group_refresh_tournament_list('')

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
        await self.request_group_refresh_tournament_list('')
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
    @database_sync_to_async
    def update_tournament_status(self):
        if self.tournament.tournament:
            self.tournament.status = TournamentConsumer.tournament_dict[self.room_group_name]['text']
            self.tournament.save() 
			
	#When receive a message
    async def receive_json(self, data):
        if 'PLAY' in data:
            TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Tournament started'
            TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 1
            msg = {'SET_BUTTON_PLAY_STATUS': {'text': TournamentConsumer.tournament_dict[self.room_group_name]['text'], 'status': TournamentConsumer.tournament_dict[self.room_group_name]['status']}}
            await self.request_group_refresh_tournament_list('')
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
				'type': 'send.group.msg.client',
				'message': message,
			}
		)
        
	#check is torunament finished
    @database_sync_to_async
    def check_tournament_finished(self):
        if Tournament_Play.objects.filter(tournament_name=self.tournament, status='WAITING').count() == 0:
            return True
        return False

	#next round
    @database_sync_to_async
    def next_round(self):
        won = Tournament_Play.objects.get(tournament_name=self.tournament, status='WON')
        waiting = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WAITING').first()
        timestamp_seconds = int(time.time())
        game_name = ""
        game_name += self.tournament.tournament
        game_name += "___"
        game_name += str(timestamp_seconds)
        #Create a new round
        tmpround = Tournament_Round()
        tmpround.tournament_name = self.tournament
        tmpround.round_name = game_name
        tmpround.player1 = won.email
        tmpround.player2 = waiting.email
        tmpround.save()
        game_name = "/game5/" + game_name
        msg = {'START_GAME': {'name': game_name, 'Player1': won.email, 'Player2': waiting.email}}
        won.status = 'PLAYING'
        won.save()
        waiting.status = 'PLAYING'
        waiting.save()
        return msg
    @database_sync_to_async
    def get_won_user(self):
        won_user = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WON').first()
        return won_user
    
    async def round_message(self, event):
        if not (await self.CheckIsTheFirstConnectedUser()):
            return
        await self.update_round(event['message'])
        data = await self.PlayModel()
        await self.request_group_refresh_tournament_status(data)
        if await self.check_tournament_finished():
            TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Tournament finished'
            TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 1
            msg = {'SET_BUTTON_PLAY_STATUS': {'text': TournamentConsumer.tournament_dict[self.room_group_name]['text'], 'status': TournamentConsumer.tournament_dict[self.room_group_name]['status']}}
            await self.request_group_refresh_tournament_list('')
            await self.send_group_msg(msg)
            won_user = await self.get_won_user()
            msg = {'TOURNAMENT_FINISHED': won_user.display_name}
            await self.send_group_msg(msg)
            await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'finish.tournament',
						'message': 'finish.tournament',
					}
				)
        else:
            msg = await self.next_round()
            #send warm message to the next players
            message_data = {
        	'room_name': 'chat_' + self.room_name,
        	'email': self.tournament.tournament,
        	'displayname': self.tournament.tournament,
        	'message': await self.get_displayname_from_email(msg['START_GAME']['Player1']) + ' and ' + await self.get_displayname_from_email(msg['START_GAME']['Player2']) + ' are the following players',
			}
            await self.channel_layer.group_send(
			'chat_' + self.room_name,
			{
				'type': 'chat.room.message',
				'message': json.dumps(message_data),
			})
            await asyncio.sleep(5)              # delay to see the winner of the round
            await self.send_group_msg(msg)
            data = await self.PlayModel()
            await self.request_group_refresh_tournament_status(data)
	
	#Receive message from the group to finish the tournament
    async def finish_tournament(self, event):
        pass
		#await self.close()
    
	# update model with the new round
    @database_sync_to_async
    def update_round(self, data):
        tmp = Tournament_Play.objects.get(tournament_name=self.tournament, email=data['winner'])
        tmp.status = 'WON'
        tmp.save()
        tmp = Tournament_Play.objects.get(tournament_name=self.tournament, status='PLAYING')
        tmp.status = 'LOST'
        tmp.save()
    
	#Receive message from the group to refresh the button play
    async def send_group_msg_client(self, event):
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
        timestamp_seconds = int(time.time())
        players = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WAITING')[:2]
        game_name = ""
        game_name += self.tournament.tournament
        game_name += "___"
        game_name += str(timestamp_seconds)
        #Create a new round
        tmpround = Tournament_Round()
        tmpround.tournament_name = self.tournament
        tmpround.round_name = game_name
        tmpround.player1 = players[0].email
        tmpround.player2 = players[1].email
        tmpround.save()
        game_name = "/game5/" + game_name
        msg = {'START_GAME': {'name': game_name, 'Player1': players[0].email, 'Player2': players[1].email}}
        return msg

	#Play command	
    async def Play(self):
        data = await self.PlayModelInit()
        await self.request_group_refresh_tournament_status(data)
        if await self.check_waiting_status():
            msg = await self.get_game_name_msg()
            await self.send_group_msg(msg)
            await self.change_status(msg['START_GAME']['Player1'], 'PLAYING')
            await self.change_status(msg['START_GAME']['Player2'], 'PLAYING')
            data = await self.PlayModel()
            await self.request_group_refresh_tournament_status(data)
            #send warm message to the next players
            message_data = {
        	'room_name': 'chat_' + self.room_name,
        	'email': self.tournament.tournament,
        	'displayname': self.tournament.tournament,
        	'message': await self.get_displayname_from_email(msg['START_GAME']['Player1']) + ' and ' + await self.get_displayname_from_email(msg['START_GAME']['Player2']) + ' are the following players',
			}
            await self.channel_layer.group_send(
			'chat_' + self.room_name,
			{
				'type': 'chat.room.message',
				'message': json.dumps(message_data),
			})
            

    @database_sync_to_async
    def get_displayname_from_email(self, email):
        try:
            tmp = User.objects.get(email=email)
            return tmp.displayname
        except:
            return "UnName"
                    
	#change status of the player
    @database_sync_to_async
    def change_status(self, player, status):
        tmp = Tournament_Play.objects.get(tournament_name=self.tournament, email=player)
        tmp.status = status
        tmp.save()

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
            TournamentConsumer.tournament_dict[self.room_group_name]['text'] = 'Waiting for players'
            TournamentConsumer.tournament_dict[self.room_group_name]['status'] = 1
        
    async def send_tournaments_with_user_count(self):
        tournaments = await self.get_tournaments_with_user_count()
        await self.send_json(tournaments)

    @database_sync_to_async
    def get_tournaments_with_user_count(self):
        tournaments_list = Tournament_List.objects.all().order_by('tournament')
        tournaments_with_count = []
        for tournament in tournaments_list:
            user_count = Tournament_Connected_Users.objects.filter(tournament_name=tournament.tournament).count()
            tournaments_with_count.append({
                'tournament_name': tournament.tournament,
                'user_count': user_count,
                'status': tournament.status  
            })
        return {'TOURNAMENT_LIST': tournaments_with_count}
    
	#send message to the group
    async def request_group_refresh_tournament_list(self, message):
        await self.update_tournament_status()
        await self.get_tournament_groups()
        
        
    async def refresh_TournamentList(self, event):
        await self.send_tournaments_with_user_count()
    @database_sync_to_async
    def get_tournament_groups(self):
        tournament_groups =  Tournament_List.objects.all().values('tournament')
        for tournament in tournament_groups:
            group_name = f"tournament_{tournament['tournament']}"
            asyncio.run(self.channel_layer.group_send(
			group_name,
			{
				'type': 'refresh.TournamentList',
				'message': group_name,
			}
		))
    	
    