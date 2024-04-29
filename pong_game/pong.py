import pygame
import random

############################### CONSTANTS & INITS ##############################

#WIDTH, HEIGHT = 1200, 900          # 4:3
WIDTH, HEIGHT = 1440, 810           # 16:9
pygame.init()
pygame.display.set_caption("Pong")
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
SCORE_FONT = pygame.font.SysFont("markerfelt", HEIGHT // 20)

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WINNING_SCORE = 10

PADDLE_WIDTH = WIDTH // 35
PADDLE_HEIGHT = HEIGHT // 5
PADDLE_GAP = WIDTH // 50            # Paddle vs screen edge gap
PADDLE_VEL = HEIGHT // 125 + 1      # Speed never 0 no matter HEIGHT
PADDLE_COLOR = BLUE
BALL_X_MAX_VEL = WIDTH // 90 + 1    # Speed never 0 no matter WIDTH
BALL_RADIUS = WIDTH // 100
BALL_COLOR = RED
BALL_VEL_INC = 1.015                # Speed increment after each paddle hit

#################################### CLASSES ###################################

class Paddle:
    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, PADDLE_COLOR, (self.x, self.y, self.width, self.height))

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
        self.x_vel = BALL_X_MAX_VEL
        self.y_vel = random.uniform(-2, 2)

    def draw(self, win):
        pygame.draw.circle(win, BALL_COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = random.uniform(-2, 2)
        self.x_vel *= -1

class Score:
    def __init__(self):
        self.left_score = 0
        self.right_score = 0
        self.won = False
        self.win_text = ""
    
    def update(self, ball):
        if ball.x < 0:
            self.right_score += 1
            ball.x_vel = BALL_X_MAX_VEL
            ball.reset()
        elif ball.x > WIDTH:
            self.left_score += 1
            ball.x_vel = BALL_X_MAX_VEL
            ball.reset()
        if self.left_score >= WINNING_SCORE:
            self.won = True
            self.win_text = "Left Player Wins!!"
        elif self.right_score >= WINNING_SCORE:
            self.won = True
            self.win_text = "Right Player Wins!!"
    
    def reset(self):
        self.left_score = 0
        self.right_score = 0
        self.won = False

################################### FUNCTIONS ##################################

def draw(win, paddles, ball, score):
    win.fill(BLACK)
    left_score_text = SCORE_FONT.render(f"{score.left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{score.right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, HEIGHT // 25))
    win.blit(right_score_text, (WIDTH * (3 / 4) - right_score_text.get_width() // 2, HEIGHT // 25))
    for paddle in paddles:
        paddle.draw(win)
    ball.draw(win)
    pygame.display.update()

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

def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w] and left_paddle.y - PADDLE_VEL >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.y + left_paddle.height + PADDLE_VEL <= HEIGHT:
        left_paddle.move(up=False)
    if keys[pygame.K_UP] and right_paddle.y - PADDLE_VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.height + PADDLE_VEL <= HEIGHT:
        right_paddle.move(up=False)

def print_winner_and_reset(left_paddle, right_paddle, ball, score):
    draw(WIN, [left_paddle, right_paddle], ball, score)
    text = SCORE_FONT.render(score.win_text, 1, WHITE)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(3000)
    ball.reset()
    ball.x_vel = BALL_X_MAX_VEL
    left_paddle.reset()
    right_paddle.reset()
    score.reset()

################################# MAIN FUNCTION ################################

def main():
    run = True
    clock = pygame.time.Clock()
    left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
    score = Score()    
    keys = pygame.key.get_pressed()
    ### GAME LOOP ###
    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                run = False
                break
        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)
        ball.move()
        handle_collision(ball, left_paddle, right_paddle)
        score.update(ball)
        if score.won:
            print_winner_and_reset(left_paddle, right_paddle, ball, score)
        print(ball.x_vel)
    pygame.quit()

if __name__ == '__main__':
    main()