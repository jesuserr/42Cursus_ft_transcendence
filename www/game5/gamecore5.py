import random
import time

############################### CONSTANTS & INITS ##############################

#WIDTH, HEIGHT = 1200, 900          # 4:3
WIDTH, HEIGHT = 1440, 810           # 16:9

FPS = 60
FRAME_TIME = 1.0 / FPS
WINNING_SCORE = 7
PLAYER_1 = 1
PLAYER_2 = 2
VOYEUR = 3
DISCONNECTED = 0

PADDLE_WIDTH = WIDTH // 35
PADDLE_HEIGHT = HEIGHT // 5
PADDLE_GAP = WIDTH // 70            # Paddle vs screen edge gap
PADDLE_VEL = HEIGHT // 125 + 1      # Speed never 0 no matter HEIGHT
BALL_X_MAX_VEL = 0.9 * WIDTH // 90 + 1    # Speed never 0 no matter WIDTH
BALL_RADIUS = WIDTH // 100
BALL_VEL_INC = 1.015                # Speed increment after each paddle hit

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

class Ball:
    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = random.choice([-BALL_X_MAX_VEL, BALL_X_MAX_VEL])
        self.y_vel = random.uniform(-BALL_X_MAX_VEL // 8, BALL_X_MAX_VEL // 8)
        self.ace = True

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.x_vel *= -1
        self.y_vel = random.uniform(-BALL_X_MAX_VEL // 8, BALL_X_MAX_VEL // 8)
        self.ace = True

class Score:
    def __init__(self):
        self.left_score = 0
        self.right_score = 0
        self.won = False
        self.left_hits = 0
        self.right_hits = 0
        self.left_aces = 0
        self.right_aces = 0
        self.game_start_time = 0        
        self.last_taken_time = 0
        self.point_length = []
    
    def update(self, ball):
        if ball.x < 0:
            self.right_score += 1
            ball.x_vel = -1 * BALL_X_MAX_VEL
            if ball.ace:
                self.right_aces += 1
            current_time = time.time()
            self.point_length.append(current_time - self.last_taken_time)
            self.last_taken_time = current_time
            ball.reset()
        elif ball.x > WIDTH:
            self.left_score += 1
            ball.x_vel = BALL_X_MAX_VEL
            if ball.ace:
                self.left_aces += 1
            current_time = time.time()
            self.point_length.append(current_time - self.last_taken_time)
            self.last_taken_time = current_time
            ball.reset()
        if self.left_score >= WINNING_SCORE:
            self.won = True
        elif self.right_score >= WINNING_SCORE:
            self.won = True

################################### FUNCTIONS ##################################

def handle_left_paddle_movement(key_states, left_paddle):
    if key_states.get('KeyW') and left_paddle.y - PADDLE_VEL >= 0:
        left_paddle.move(up=True)
    if key_states.get('KeyS') and left_paddle.y + left_paddle.height + PADDLE_VEL <= HEIGHT:
        left_paddle.move(up=False)    

def handle_right_paddle_movement(key_states, right_paddle):
    if key_states.get('ArrowUp') and right_paddle.y - PADDLE_VEL >= 0:
        right_paddle.move(up=True)
    if key_states.get('ArrowDown') and right_paddle.y + right_paddle.height + PADDLE_VEL <= HEIGHT:
        right_paddle.move(up=False)

def handle_collision(ball, left_paddle, right_paddle, score):
    if ball.y + ball.radius > HEIGHT:
        ball.y_vel *= -1
        ball.ace = False
        return
    elif ball.y - ball.radius < 0:
        ball.y_vel *= -1
        ball.ace = False
        return
    if ball.x_vel < 0:
        if ball.y + ball.radius >= left_paddle.y and ball.y - ball.radius <= left_paddle.y + left_paddle.height and \
        ball.x - ball.radius <= left_paddle.x + left_paddle.width and ball.x - ball.radius >= left_paddle.x:
            ball.x_vel *= -BALL_VEL_INC
            difference_in_y = ball.y - left_paddle.y - left_paddle.height / 2
            reduction_factor = (left_paddle.height / 2) / BALL_X_MAX_VEL
            ball.y_vel = difference_in_y / reduction_factor
            score.left_hits += 1
            ball.ace = True
    else:
        if ball.y + ball.radius >= right_paddle.y and ball.y - ball.radius <= right_paddle.y + right_paddle.height and \
        ball.x + ball.radius >= right_paddle.x and ball.x + ball.radius <= right_paddle.x + right_paddle.width:
            ball.x_vel *= -BALL_VEL_INC
            difference_in_y = ball.y - right_paddle.y - right_paddle.height / 2
            reduction_factor = (right_paddle.height / 2) / BALL_X_MAX_VEL
            ball.y_vel = difference_in_y / reduction_factor
            score.right_hits += 1
            ball.ace = True