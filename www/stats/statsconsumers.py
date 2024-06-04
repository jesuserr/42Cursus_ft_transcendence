import json
import asyncio
import time
import copy                         # To copy classes without copy constructor
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from . import statscore
from .statscore import *

class StatsConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_states = {}
        self.players = 0
    
    async def connect(self):    
        self.room_name = self.scope["url_route"]["kwargs"]["stats_name"]
        self.room_group_name = f"game_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        asyncio.ensure_future(self.playGame())      # Init game

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        self.key_states = json.loads(text_data)

    async def send_gameboard(self, ball, l_paddle, r_paddle, score):
        gameboard = {
            "width": WIDTH, "height": HEIGHT, "ball_x_speed": ball.x_vel,
            "ball_x": int(ball.x), "ball_y": int(ball.y), "ball_radius": ball.radius,
            "left_paddle_x": l_paddle.x, "left_paddle_y": l_paddle.y,
            "right_paddle_x": r_paddle.x, "right_paddle_y": r_paddle.y,
            "paddle_width": r_paddle.width, "paddle_height": r_paddle.height,
            "score_left": score.left_score, "score_right": score.right_score,
            "winner": score.won
            }
        await self.send(text_data=json.dumps(gameboard))

    async def waiting_players(self, ball):
        while True:
            if self.key_states:
                if 'Digit1' in self.key_states:
                    self.players = 1                # 1 -> Player vs CPU
                    return copy.copy(ball)
                elif 'Digit2' in self.key_states:   # 2 -> PvP
                    self.players = 2
                    return copy.copy(ball)          # Just returning something
            await asyncio.sleep(0.1)

    async def waiting_countdown(self):
        while True:
            if self.key_states:
                if 'F15' in self.key_states:
                    break
            await asyncio.sleep(0.1)
            
    async def playGame(self):
        left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        score = Score()
        await self.send_gameboard(ball, left_paddle, right_paddle, score)
        ball_image = await self.waiting_players(ball)
        await self.send_gameboard(ball, left_paddle, right_paddle, score)
        await self.waiting_countdown()
        last_peek_time = time.time()
        while True:                                              ### GAME LOOP ###
            frame_start_time = time.time()
            await self.send_gameboard(ball, left_paddle, right_paddle, score)
            handle_paddle_movement(self.key_states, left_paddle, right_paddle, self.players)
            if self.players == 1:
                current_time = time.time()
                if current_time - last_peek_time >= AI_TIME_INTERVAL_BALL_POS:
                    ball_image = copy.copy(ball)
                    last_peek_time = current_time
                computer_player(right_paddle, ball_image)
            ball.move()
            handle_collision(ball, left_paddle, right_paddle)
            score.update(ball)
            if score.won:
                await self.send_gameboard(ball, left_paddle, right_paddle, score)
                break
            await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.35)
            while time.time() - frame_start_time < FRAME_TIME:
               await asyncio.sleep((FRAME_TIME - (time.time() - frame_start_time)) * 0.0005)
            while (self.key_states.get('F14')):
                await self.send_gameboard(ball, left_paddle, right_paddle, score)
                await asyncio.sleep(0.1)
            #print(ball.x, ball.y, ball_image.x, ball_image.y)
            #print((time.time() - frame_start_time) * 1000, ball.x_vel, self.room_group_name)
