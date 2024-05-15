import json
import asyncio
import time
import copy
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from . import total_pong_no_drawing2
from .total_pong_no_drawing2 import *

class GameConsumer2(AsyncWebsocketConsumer):
    rooms = {}

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.room_group_name = f"game_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        if self.room_group_name not in self.rooms.keys():
            self.rooms[self.room_group_name] = {"players": {"player1": self}}
            self.rooms[self.room_group_name]["key_states_1"] = {}
        else:
            self.rooms[self.room_group_name]['players']['player2'] = self
            self.rooms[self.room_group_name]["key_states_2"] = {}
            asyncio.ensure_future(self.playGame())                  # Init game
        #print("Players Info: " + str(self.rooms[self.room_group_name]))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        players = self.rooms[self.room_group_name]['players']           # kind of alias
        if players['player1'] == self:
            self.rooms[self.room_group_name]['key_states_1'] = json.loads(text_data)
        elif players.get('player2') == self:
            self.rooms[self.room_group_name]['key_states_2'] = json.loads(text_data)        

    async def send_gameboard(self, ball, l_paddle, r_paddle, score, player, paused):
        gameboard = {
            "width": WIDTH, "height": HEIGHT, "ball_x_speed": ball.x_vel,
            "ball_x": int(ball.x), "ball_y": int(ball.y), "ball_radius": ball.radius,
            "left_paddle_x": l_paddle.x, "left_paddle_y": l_paddle.y,
            "right_paddle_x": r_paddle.x, "right_paddle_y": r_paddle.y,
            "paddle_width": r_paddle.width, "paddle_height": r_paddle.height,
            "score_left": score.left_score, "score_right": score.right_score,
            "winner": score.won, "player": player, "paused": paused
            }
        await self.send(text_data=json.dumps(gameboard))

    async def waiting_countdown(self):
        while True:
            if self.rooms[self.room_group_name]['key_states_1'] and self.rooms[self.room_group_name]['key_states_2']:
                if 'F15' in self.rooms[self.room_group_name]['key_states_1'] and 'F15' in self.rooms[self.room_group_name]['key_states_2']:
                    break
            await asyncio.sleep(0.1)
            
    async def playGame(self):
        left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        score = Score()        
        await self.rooms[self.room_group_name]['players']['player1'].send_gameboard(ball, left_paddle, right_paddle, score, 1, False)
        await self.rooms[self.room_group_name]['players']['player2'].send_gameboard(ball, left_paddle, right_paddle, score, 2, False)
        await self.waiting_countdown()
        while True:
            frame_start_time = time.time()
            await self.rooms[self.room_group_name]['players']['player1'].send_gameboard(ball, left_paddle, right_paddle, score, 1, False)
            await self.rooms[self.room_group_name]['players']['player2'].send_gameboard(ball, left_paddle, right_paddle, score, 2, False)
            handle_left_paddle_movement(self.rooms[self.room_group_name]['key_states_1'], left_paddle)
            handle_right_paddle_movement(self.rooms[self.room_group_name]['key_states_2'], right_paddle)
            ball.move()
            handle_collision(ball, left_paddle, right_paddle)
            score.update(ball)
            if score.won:
                await self.rooms[self.room_group_name]['players']['player1'].send_gameboard(ball, left_paddle, right_paddle, score, 1, False)
                await self.rooms[self.room_group_name]['players']['player2'].send_gameboard(ball, left_paddle, right_paddle, score, 2, False)
                break
            await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.35)
            while time.time() - frame_start_time < FRAME_TIME:
               await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.0005)
            while (self.rooms[self.room_group_name]['key_states_1'].get('F14') or self.rooms[self.room_group_name]['key_states_2'].get('F14')):
                await self.rooms[self.room_group_name]['players']['player1'].send_gameboard(ball, left_paddle, right_paddle, score, 1, True)
                await self.rooms[self.room_group_name]['players']['player2'].send_gameboard(ball, left_paddle, right_paddle, score, 2, True)                
                await asyncio.sleep(0.1)