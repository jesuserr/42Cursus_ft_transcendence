import json
import asyncio
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from . import gamecore5
from .gamecore5 import *
from .models import stats
from channels.db import database_sync_to_async
from main.models import User
#from main.token import *                   -> makes time.time() crash
from main.token import get_user_from_token  # solution
from tournament.models import Tournament_List, Tournament_Round, Tournament_Play

class GameConsumer5(AsyncWebsocketConsumer):
    rooms = {}  # Class variable shared by all instances of this class
                # aliases used in code below cannot be used when there is an assignment

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.room_group_name = f"game_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        if 'tokenid' in self.scope['cookies'].keys():
            await self.getUsernameModel()
            await self.accept()
            self.left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
            self.right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
            self.ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
            self.score = Score()
            gameboard = await self.create_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score)
            validUser = await self.isValidUser()                # Has to be checked here or fails if checked inside the if statements
            if not validUser:
                await self.send_gameboard(gameboard, VOYEUR)
            elif self.room_group_name not in self.rooms.keys() and validUser:
                self.rooms[self.room_group_name] = {"players": {"player1": self}}
                self.rooms[self.room_group_name]["key_states_1"] = {}
                self.rooms[self.room_group_name]["player1_connected"] = True
                self.rooms[self.room_group_name]["player2_connected"] = False
                self.rooms[self.room_group_name]["player1_id"] = self.user
                self.rooms[self.room_group_name]["player1_nick"] = self.user.displayname
                await self.rooms[self.room_group_name]['players']['player1'].send_gameboard(gameboard, PLAYER_1)
            elif self.rooms[self.room_group_name]["player2_connected"] == False and self.rooms[self.room_group_name]["player1_id"] != self.user and validUser:            
                self.rooms[self.room_group_name]['players']['player2'] = self
                self.rooms[self.room_group_name]["key_states_2"] = {}
                self.rooms[self.room_group_name]["player2_connected"] = True
                self.rooms[self.room_group_name]["player2_id"] = self.user
                self.rooms[self.room_group_name]["player2_nick"] = self.user.displayname
                await self.rooms[self.room_group_name]['players']['player2'].send_gameboard(gameboard, PLAYER_2)
                asyncio.ensure_future(self.playGame())                      # Init game on players2 instance
            #print("Players Info: " + str(self.rooms[self.room_group_name]))

    @database_sync_to_async
    def getUsernameModel(self):
        try:
            token = self.scope['cookies']['tokenid']
            self.user = get_user_from_token(token)
        except:
            self.user = ""

    async def disconnect(self, close_code):
        if not await self.isValidUser():
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            return
        players = self.rooms[self.room_group_name]['players']           # alias
        room = self.rooms[self.room_group_name]                         # alias
        if 'player1' in players and players['player1'] == self:
            self.rooms[self.room_group_name]["player1_connected"] = False
        if 'player2' in players and players['player2'] == self:
            self.rooms[self.room_group_name]["player2_connected"] = False
        if not room["player2_connected"] and not room["player1_connected"]:
            del self.rooms[self.room_group_name]                        # delete room_group_name from dictionary when both players disconnect
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        players = self.rooms[self.room_group_name]['players']           # alias
        if players['player1'] == self:
            self.rooms[self.room_group_name]['key_states_1'] = json.loads(text_data)
        elif players['player2'] == self:
            self.rooms[self.room_group_name]['key_states_2'] = json.loads(text_data)
            
    @database_sync_to_async
    def isValidUser(self):
        self.tournament = Tournament_List.objects.get(tournament = self.room_name.split('___')[0])
        tmpplay = Tournament_Round.objects.filter(tournament_name=self.tournament, round_name=self.room_name).first()
        if (tmpplay.player1 == self.user.email or tmpplay.player2 == self.user.email):
            return True
        return False

    async def create_gameboard(self, ball, l_paddle, r_paddle, score):
        gameboard = {
            "width": WIDTH, "height": HEIGHT, "ball_x_speed": ball.x_vel,
            "ball_x": int(ball.x), "ball_y": int(ball.y), "ball_radius": ball.radius,
            "left_paddle_x": l_paddle.x, "left_paddle_y": l_paddle.y,
            "right_paddle_x": r_paddle.x, "right_paddle_y": r_paddle.y,
            "paddle_width": r_paddle.width, "paddle_height": r_paddle.height,
            "score_left": score.left_score, "score_right": score.right_score,
            "winner": score.won
            }
        if self.rooms.get(self.room_group_name) and self.rooms[self.room_group_name]["player2_connected"] == True:
            gameboard["p1_nick"] = str(self.rooms[self.room_group_name]["player1_nick"])
            gameboard["p2_nick"] = str(self.rooms[self.room_group_name]["player2_nick"])
        return gameboard

    async def send_gameboard_to_group(self, event):
        if (self.user == self.rooms[self.room_group_name]["player1_id"]):
            await self.send_gameboard(event['gameboard'], PLAYER_1)
        elif (self.user == self.rooms[self.room_group_name]["player2_id"]):
            await self.send_gameboard(event['gameboard'], PLAYER_2)
        else:
            await self.send_gameboard(event['gameboard'], VOYEUR)

    async def send_gameboard(self, gameboard, player):
        gameboard["player"] = player
        await self.send(text_data=json.dumps(gameboard))

    async def waiting_countdown(self):
        room = self.rooms[self.room_group_name]                         # alias
        while room["player2_connected"] and room["player1_connected"]:
            if room['key_states_1'] and room['key_states_2']:
                if 'F15' in room['key_states_1'] and 'F15' in room['key_states_2']:
                    break
            await asyncio.sleep(0.1)

    async def managing_disconnection(self):
        room = self.rooms[self.room_group_name]                         # alias
        if not room["player2_connected"]:
            self.score.left_score = WINNING_SCORE
            self.score.right_score = 0
        elif not room["player1_connected"]:
            self.score.right_score = WINNING_SCORE
            self.score.left_score = 0
        self.score.won = True
            
    async def playGame(self):
        players = self.rooms[self.room_group_name]['players']           # alias
        room = self.rooms[self.room_group_name]                         # alias
        gameboard = await self.create_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score)
        await self.channel_layer.group_send(self.room_group_name,{'type': 'send_gameboard_to_group','message': '','gameboard': gameboard})
        await self.waiting_countdown()
        self.score.game_start_time = self.score.last_taken_time = time.time()
        while True:
            frame_start_time = time.time()
            gameboard = await self.create_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score)
            if not room["player2_connected"] or not room["player1_connected"]:      # check if any player got disconnected
                await self.managing_disconnection()
                await players['player1'].send_gameboard(gameboard, DISCONNECTED)
                await players['player2'].send_gameboard(gameboard, DISCONNECTED)
                break
            else:                
                await self.channel_layer.group_send(self.room_group_name,{'type': 'send_gameboard_to_group','message': '','gameboard': gameboard})
            handle_left_paddle_movement(room['key_states_1'], self.left_paddle)
            handle_right_paddle_movement(room['key_states_2'], self.right_paddle)
            self.ball.move()
            handle_collision(self.ball, self.left_paddle, self.right_paddle, self.score)
            self.score.update(self.ball)
            if self.score.won:
                gameboard = await self.create_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score)
                await self.channel_layer.group_send(self.room_group_name,{'type': 'send_gameboard_to_group','message': '','gameboard': gameboard})
                break
            await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.2)
            while time.time() - frame_start_time < FRAME_TIME:
               await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.0002)
        await self.SendRoundEndMSG()
        tournament_winner = await self.whoWonTournament()
        await self.pushStats(room, self.score, tournament_winner)
        await self.channel_layer.group_send(self.room_group_name, {'type': 'close_all_connections', 'message': ''}) # close all websocket connections

    async def SendRoundEndMSG(self):
        room = self.rooms[self.room_group_name]
        data = self.room_name.split('___')
        tournament_name = 'tournament_'
        tournament_name += data[0]
        if self.score.left_score > self.score.right_score:
            winner = room["player1_id"].email
        else:
            winner = room["player2_id"].email
        msg = {'round': self.room_name, 'winner': winner}
        await self.channel_layer.group_send(
            tournament_name,
            {
                'type': 'round_message',
                'message': msg
            }
        )

    async def whoWonTournament(self):
        await asyncio.sleep(1)
        if (await self.whoWonTournamentModel(1) == True):
            return await self.whoWonTournamentModel(2)
        return None

    @database_sync_to_async
    def whoWonTournamentModel(self, option):
        if (option == 1):
            self.tournament = Tournament_List.objects.get(tournament = self.room_name.split('___')[0])
            waiting_count = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WAITING').count()
            playing_count = Tournament_Play.objects.filter(tournament_name=self.tournament, status='PLAYING').count()
            if (waiting_count == 0 and playing_count == 0):
                return True
            return False
        if (option == 2):
                tmp = Tournament_Play.objects.filter(tournament_name=self.tournament, status='WON').first()
                return tmp.email
        return None
    
    @database_sync_to_async
    def pushStats(self, room, score, tournament_winner):
        match_length = time.time() - score.game_start_time
        temp = stats(player_one = room["player1_id"])               # player 1 stats
        temp.match_length = match_length
        temp.player_one_score = score.left_score
        temp.player_one_hits = score.left_hits
        temp.player_one_aces = score.left_aces
        temp.player_two = room["player2_id"]        
        temp.player_two_score = score.right_score
        temp.player_two_hits = score.right_hits
        temp.player_two_aces = score.right_aces
        temp.point_length = score.point_length
        if score.left_score > score.right_score:
            temp.player_one_win = temp.tournament = True
        else:
            temp.player_two_win = temp.tournament = True
        temp.tournament_name = str(self.room_name.split('___')[0])
        if (tournament_winner == str(room["player1_id"])):
            temp.player_one_tournament_win = True
        elif (tournament_winner == str(room["player2_id"])): 
            temp.player_two_tournament_win = True
        temp.save()
        temp = stats(player_one = room["player2_id"])               # player 2 stats
        temp.match_length = match_length
        temp.player_one_score = score.right_score
        temp.player_one_hits = score.right_hits
        temp.player_one_aces = score.right_aces
        temp.player_two = room["player1_id"]        
        temp.player_two_score = score.left_score
        temp.player_two_hits = score.left_hits
        temp.player_two_aces = score.left_aces
        temp.point_length = score.point_length
        if score.left_score > score.right_score:
            temp.player_two_win = temp.tournament = True
        else:
            temp.player_one_win = temp.tournament = True
        temp.tournament_name = str(self.room_name.split('___')[0])
        if (tournament_winner == str(room["player1_id"])):
            temp.player_two_tournament_win = True
        elif (tournament_winner == str(room["player2_id"])): 
            temp.player_one_tournament_win = True
        temp.save()

    async def close_all_connections(self, event):
        await self.close()
        print("Connection Closed")