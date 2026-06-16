import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player_x = 100
player_y = 50
vel_y = 0
gravity = 0.5

collision_img = pygame.Surface((WIDTH, HEIGHT))
collision_img.fill((0, 0, 0))

for x in range(WIDTH):
    pygame.draw.line(collision_img, (255,255,255), (x,350), (x,350))

def get_ground_y(x):
    for y in range(HEIGHT):
        if collision_img.get_at((x, y)) == (255, 255, 255):
            return y
    return HEIGHT

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player_x -= 4
    if keys[pygame.K_RIGHT]:
        player_x += 4

    vel_y += gravity
    player_y += vel_y

    ground_y = get_ground_y(int(player_x))

    if player_y >= ground_y:
        player_y = ground_y
        vel_y = 0

    screen.fill((30, 30, 30))

    pygame.draw.line(screen, (255, 255, 255), (0, 350), (WIDTH, 350), 2)
    pygame.draw.rect(screen, (160, 0, 255), (player_x, player_y - 20, 30, 30))

    pygame.display.update()
    clock.tick(60)