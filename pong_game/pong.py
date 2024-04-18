import pygame

############################### CONSTANTS & INITS ##############################

WIDTH, HEIGHT = 1200, 900
pygame.init()
pygame.display.set_caption("Pong")
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
SCORE_FONT = pygame.font.SysFont("markerfelt", HEIGHT // 20)

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

PADDLE_WIDTH = WIDTH // 35
PADDLE_HEIGHT = HEIGHT // 5
PADDLE_GAP = WIDTH // 25
BALL_RADIUS = WIDTH // 100
WINNING_SCORE = 10

#################################### CLASSES ###################################

class Paddle:
    COLOR = BLUE
    VEL = HEIGHT // 166 + 1                     ## Speed never 0 no matter HEIGHT
    
    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))
        
    def move(self, up):
        if up == True:
            self.y -= self.VEL
        else:
            self.y += self.VEL
    
    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    COLOR = RED
    MAX_VEL = HEIGHT // 75 + 1                  ## Speed never 0 no matter HEIGHT

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
    
    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        self.x_vel *= -1

################################### FUNCTIONS ##################################

def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)
    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
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
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height and \
        ball.x - ball.radius <= left_paddle.x + left_paddle.width and \
        ball.x - ball.radius >= left_paddle.x:
            ball.x_vel *= -1
            middle_y = left_paddle.y + left_paddle.height / 2
            difference_in_y = middle_y - ball.y
            reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
            y_vel = difference_in_y / reduction_factor
            ball.y_vel = -1 * y_vel
    else:
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height and \
        ball.x + ball.radius >= right_paddle.x and \
        ball.x + ball.radius <= right_paddle.x + right_paddle.width:
            ball.x_vel *= -1
            middle_y = right_paddle.y + right_paddle.height / 2
            difference_in_y = middle_y - ball.y
            reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
            y_vel = difference_in_y / reduction_factor
            ball.y_vel = -1 * y_vel

def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.y + left_paddle.height + left_paddle.VEL <= HEIGHT:
        left_paddle.move(up=False)
    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.height + right_paddle.VEL <= HEIGHT:
        right_paddle.move(up=False)

################################# MAIN FUNCTION ################################

def main():
    run = True
    clock = pygame.time.Clock()
    left_paddle = Paddle(PADDLE_GAP, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - PADDLE_GAP - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
    left_score = 0
    right_score = 0
    won = False
    keys = pygame.key.get_pressed()

    ### GAME LOOP ###
    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                run = False
                break
        
        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)
        ball.move()
        handle_collision(ball, left_paddle, right_paddle)

        if ball.x < 0:
            right_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()

        if left_score >= WINNING_SCORE:
            won = True
            win_text = "Left Player Wins!!"
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "Right Player Wins!!"

        if won:
            draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)
            text = SCORE_FONT.render(win_text, 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0
            won = False

    pygame.quit()

if __name__ == '__main__':
    main()