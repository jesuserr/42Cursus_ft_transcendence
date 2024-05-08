import json
import asyncio
import time
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from . import total_pong_no_drawing
from .total_pong_no_drawing import *

key_states = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.room_group_name = f"game_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        #iniciar el loop del juego
        asyncio.ensure_future(self.playGame())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        global key_states
        key_states = json.loads(text_data)

    async def send_gameboard(self, ball, l_paddle, r_paddle, score):
        gameboard = {
            "width": WIDTH, "height": HEIGHT,
            "ball_x": ball.x, "ball_y": ball.y, "ball_radius": ball.radius,
            "left_paddle_x": l_paddle.x, "left_paddle_y": l_paddle.y,
            "right_paddle_x": r_paddle.x, "right_paddle_y": r_paddle.y,
            "paddle_width": r_paddle.width, "paddle_height": r_paddle.height,
            "score_left": score.left_score, "score_right": score.right_score,
            }
        await self.send(text_data=json.dumps(gameboard))
        await asyncio.sleep(1 / 600)

    async def playGame(self):
        left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        if PLAYERS == 1:
            ball_image = copy.copy(ball)
        score = Score()
        last_peek_time = time.time()
        run = True
        while run:                                              ### GAME LOOP ###
            frame_start_time = time.time()
            await self.send_gameboard(ball, left_paddle, right_paddle, score)
            handle_paddle_movement(key_states, left_paddle, right_paddle, PLAYERS)
            if PLAYERS == 1:
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
                print_winner_and_reset(left_paddle, right_paddle, ball, score)
            frame_duration = time.time() - frame_start_time
            while frame_duration < FRAME_TIME:
               time.sleep((FRAME_TIME - frame_duration) * 0.75)
               frame_duration = time.time() - frame_start_time