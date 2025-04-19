import pygame
import sys

# 초기화
pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("벽돌깨기 게임")

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 102, 204)
RED = (255, 0, 0)

# 패들
paddle = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 30, 100, 10)
paddle_speed = 7

# 공
ball = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2 - 10, 20, 20)
ball_speed = [5, -5]

# 벽돌
bricks = []
brick_rows, brick_cols = 5, 7
brick_width = WIDTH // brick_cols
brick_height = 30
for row in range(brick_rows):
    for col in range(brick_cols):
        brick = pygame.Rect(col * brick_width, row * brick_height + 40, brick_width - 2, brick_height - 2)
        bricks.append(brick)

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 패들 이동
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.left -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.right += paddle_speed

    # 공 이동
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # 벽과 충돌
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top <= 0:
        ball_speed[1] = -ball_speed[1]
    if ball.colliderect(paddle):
        ball_speed[1] = -ball_speed[1]
    if ball.bottom >= HEIGHT:
        print("Game Over")
        running = False

    # 벽돌과 충돌
    hit_index = ball.collidelist(bricks)
    if hit_index != -1:
        del bricks[hit_index]
        ball_speed[1] = -ball_speed[1]

    # 그리기
    pygame.draw.rect(screen, BLUE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)

    # 승리 조건
    if not bricks:
        print("You Win!")
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()