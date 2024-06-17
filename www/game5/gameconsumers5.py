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
            if self.room_group_name not in self.rooms.keys():
                self.rooms[self.room_group_name] = {"players": {"player1": self}}
                self.rooms[self.room_group_name]["key_states_1"] = {}
                self.rooms[self.room_group_name]["player1_connected"] = True
                self.rooms[self.room_group_name]["player2_connected"] = False
                self.rooms[self.room_group_name]["player1_id"] = self.user
                await self.rooms[self.room_group_name]['players']['player1'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_1)
            elif self.rooms[self.room_group_name]["player2_connected"] == False and self.rooms[self.room_group_name]["player1_id"] != self.user:
                self.rooms[self.room_group_name]['players']['player2'] = self
                self.rooms[self.room_group_name]["key_states_2"] = {}
                self.rooms[self.room_group_name]["player2_connected"] = True
                self.rooms[self.room_group_name]["player2_id"] = self.user
                await self.rooms[self.room_group_name]['players']['player2'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_2)
                asyncio.ensure_future(self.playGame())                      # Init game on players2 instance
            #print("Players Info: " + str(self.rooms[self.room_group_name]))

    @database_sync_to_async
    def getUsernameModel(self):
        try:
            token = self.scope['cookies']['tokenid']
            self.user = get_user_from_token(token)
            #print(self.user.__dict__)
        except:
            self.user = ""

    async def disconnect(self, close_code):
        players = self.rooms[self.room_group_name]['players']           # alias
        room = self.rooms[self.room_group_name]                         # alias
        if players['player1'] == self:
            self.rooms[self.room_group_name]["player1_connected"] = False
        elif players['player2'] == self:
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

    async def send_gameboard(self, ball, l_paddle, r_paddle, score, player):
        gameboard = {
            "width": WIDTH, "height": HEIGHT, "ball_x_speed": ball.x_vel,
            "ball_x": int(ball.x), "ball_y": int(ball.y), "ball_radius": ball.radius,
            "left_paddle_x": l_paddle.x, "left_paddle_y": l_paddle.y,
            "right_paddle_x": r_paddle.x, "right_paddle_y": r_paddle.y,
            "paddle_width": r_paddle.width, "paddle_height": r_paddle.height,
            "score_left": score.left_score, "score_right": score.right_score,
            "winner": score.won, "player": player
            }
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
        await players['player1'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_1)
        await players['player2'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_2)
        await self.waiting_countdown()
        self.score.game_start_time = self.score.last_taken_time = time.time()
        while True:
            frame_start_time = time.time()
            if not room["player2_connected"] or not room["player1_connected"]:      # check if any player got disconnected
                await self.managing_disconnection()
                await players['player1'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, DISCONNECTED)
                await players['player2'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, DISCONNECTED)
                break
            else:
                await players['player1'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_1)
                await players['player2'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_2)
            handle_left_paddle_movement(room['key_states_1'], self.left_paddle)
            handle_right_paddle_movement(room['key_states_2'], self.right_paddle)
            self.ball.move()
            handle_collision(self.ball, self.left_paddle, self.right_paddle, self.score)
            self.score.update(self.ball)
            if self.score.won:
                await players['player1'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_1)
                await players['player2'].send_gameboard(self.ball, self.left_paddle, self.right_paddle, self.score, PLAYER_2)
                break
            await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.2)
            while time.time() - frame_start_time < FRAME_TIME:
               await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.0002)
        await self.pushStats(room, self.score)
        await players['player1'].close()                                # close websocket connections
        await players['player2'].close()

    @database_sync_to_async
    def pushStats(self, room, score):
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
        temp.save()