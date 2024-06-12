import time
import copy                         # To copy classes without copy constructor
import random
import asyncio
import json
import websockets

############################### CONSTANTS & INITS ##############################

#WIDTH, HEIGHT = 1200, 900          # 4:3
WIDTH, HEIGHT = 1440, 810           # 16:9

FPS = 60
FRAME_TIME = 1.0 / FPS
WINNING_SCORE = 10

PADDLE_WIDTH = WIDTH // 35
PADDLE_HEIGHT = HEIGHT // 5
PADDLE_GAP = WIDTH // 50            # Paddle vs screen edge gap
PADDLE_VEL = HEIGHT // 125 + 1      # Speed never 0 no matter HEIGHT
BALL_X_MAX_VEL = WIDTH // 90 + 1    # Speed never 0 no matter WIDTH
BALL_RADIUS = WIDTH // 100
BALL_VEL_INC = 1.015                # Speed increment after each paddle hit
AI_TIME_INTERVAL_BALL_POS = 1       # AI interval time to check ball pos in secs
PLAYERS = 1                         # 1 -> Player vs CPU // 2 -> PvP

#################################### CLASSES ###################################

class Paddle:
    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def move(self, up):
        if up == True:
            self.y -= PADDLE_VEL
        else:
            self.y += PADDLE_VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = random.choice([-BALL_X_MAX_VEL, BALL_X_MAX_VEL])
        self.y_vel = random.uniform(-BALL_X_MAX_VEL // 8, BALL_X_MAX_VEL // 8)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.x_vel *= -1
        self.y_vel = random.uniform(-BALL_X_MAX_VEL // 8, BALL_X_MAX_VEL // 8)        

class Score:
    def __init__(self):
        self.left_score = 0
        self.right_score = 0
        self.won = False        
    
    def update(self, ball):
        if ball.x < 0:
            self.right_score += 1
            ball.x_vel = -1 * BALL_X_MAX_VEL
            ball.reset()
        elif ball.x > WIDTH:
            self.left_score += 1
            ball.x_vel = BALL_X_MAX_VEL
            ball.reset()
        if self.left_score >= WINNING_SCORE:
            self.won = True
        elif self.right_score >= WINNING_SCORE:
            self.won = True
    
    def reset(self):
        self.left_score = 0
        self.right_score = 0
        self.won = False

################################### FUNCTIONS ##################################

def handle_paddle_movement(key_states, left_paddle, right_paddle, players):
    if key_states.get('KeyW') and left_paddle.y - PADDLE_VEL >= 0:
        left_paddle.move(up=True)
    if key_states.get('KeyS') and left_paddle.y + left_paddle.height + PADDLE_VEL <= HEIGHT:
        left_paddle.move(up=False)
    if players == 2:
        if key_states.get('ArrowUp') and right_paddle.y - PADDLE_VEL >= 0:
            right_paddle.move(up=True)
        if key_states.get('ArrowDown') and right_paddle.y + right_paddle.height + PADDLE_VEL <= HEIGHT:
            right_paddle.move(up=False)

def computer_player(right_paddle, ball_image):
    if ball_image.x_vel < 0:                  # Paddle back to center pos when ball goes left, removing this would be easier level
        if (right_paddle.y + right_paddle.height // 2 > HEIGHT // 2):
            right_paddle.move(up=True)
        if (right_paddle.y + right_paddle.height // 2 < HEIGHT // 2):
            right_paddle.move(up=False)
    else:                                       # Less challenging if 0.15 and 0.85 are 0.5 (center of the paddle)
        paddle_impact_point = ball_image.y + (((right_paddle.x - ball_image.x) / ball_image.x_vel) * ball_image.y_vel)
        if paddle_impact_point < 0:
            paddle_impact_point = -1 * paddle_impact_point
        if paddle_impact_point > HEIGHT:
            paddle_impact_point = (2 * HEIGHT) - paddle_impact_point
        if paddle_impact_point < right_paddle.y + right_paddle.height * 0.15 and right_paddle.y - PADDLE_VEL >= 0:
            right_paddle.move(up=True)
        if paddle_impact_point > right_paddle.y + right_paddle.height * 0.85 and right_paddle.y + right_paddle.height + PADDLE_VEL <= HEIGHT:
            right_paddle.move(up=False)

def handle_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius > HEIGHT:
        ball.y_vel *= -1
        return              ## Return to avoid ball trapped at bottom (Iria bug)
    elif ball.y - ball.radius < 0:
        ball.y_vel *= -1
        return              ## Return to avoid ball trapped at top (Iria bug)
    if ball.x_vel < 0:
        if ball.y + ball.radius >= left_paddle.y and ball.y - ball.radius <= left_paddle.y + left_paddle.height and \
        ball.x - ball.radius <= left_paddle.x + left_paddle.width and ball.x - ball.radius >= left_paddle.x:
            ball.x_vel *= -BALL_VEL_INC
            difference_in_y = ball.y - left_paddle.y - left_paddle.height / 2
            reduction_factor = (left_paddle.height / 2) / BALL_X_MAX_VEL
            ball.y_vel = difference_in_y / reduction_factor             
    else:
        if ball.y + ball.radius >= right_paddle.y and ball.y - ball.radius <= right_paddle.y + right_paddle.height and \
        ball.x + ball.radius >= right_paddle.x and ball.x + ball.radius <= right_paddle.x + right_paddle.width:
            ball.x_vel *= -BALL_VEL_INC
            difference_in_y = ball.y - right_paddle.y - right_paddle.height / 2
            reduction_factor = (right_paddle.height / 2) / BALL_X_MAX_VEL
            ball.y_vel = difference_in_y / reduction_factor   

def print_winner_and_reset(left_paddle, right_paddle, ball, score):
    time.sleep(3)
    ball.reset()
    ball.x_vel = random.choice([-BALL_X_MAX_VEL, BALL_X_MAX_VEL])
    left_paddle.reset()
    right_paddle.reset()
    score.reset()

################################# MAIN FUNCTION ################################

async def send_gameboard(websocket, ball, l_paddle, r_paddle, score):
    gameboard = {
        "width": WIDTH, "height": HEIGHT,
        "ball_x": ball.x, "ball_y": ball.y, "ball_radius": ball.radius,
        "left_paddle_x": l_paddle.x, "left_paddle_y": l_paddle.y,
        "right_paddle_x": r_paddle.x, "right_paddle_y": r_paddle.y,
        "paddle_width": r_paddle.width, "paddle_height": r_paddle.height,
        "score_left": score.left_score, "score_right": score.right_score,
        }
    await websocket.send(json.dumps(gameboard))    

async def main(websocket):
    left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
    ball_image = copy.copy(ball)
    score = Score()
    key_states = {}
    last_peek_time = time.time()
    run = True
    while run:                                              ### GAME LOOP ###
        frame_start_time = time.time()
        await send_gameboard(websocket, ball, left_paddle, right_paddle, score)
        try:
            key_states = json.loads(await asyncio.wait_for(websocket.recv(), timeout=0.0001))
        except asyncio.TimeoutError:
            pass
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
            await send_gameboard(websocket, ball, left_paddle, right_paddle, score)
            print_winner_and_reset(left_paddle, right_paddle, ball, score)
        frame_duration = time.time() - frame_start_time
        while frame_duration < FRAME_TIME:
            time.sleep((FRAME_TIME - frame_duration) * 0.75)
            frame_duration = time.time() - frame_start_time        

async def start_server():
    async with websockets.serve(main, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start_server())