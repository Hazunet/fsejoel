from pygame import *
from math import *
import random

init()
w, h = 1200, 900
screen = display.set_mode((w, h))

grey = (127, 127, 127)
blue = (0, 0, 255)
white = (255, 255, 255)
dirt = (109, 36, 0)
red = (255, 0, 0)

X = 0
Y = 1
W = 2
H = 3
ROW = 4
COL = 5

bg_img = transform.scale(image.load("pics/Sonic BG final.png"), (36720, 4590))

def add_pics(folder, name, start, end):
    pics = []
    for i in range(start, end):
        pics.append(image.load(f"pics/{folder}/{name}{i}.png"))
    return pics

sonic_right = add_pics("sonic sprites", "sonic", 1, 10)
sonic_left  = [transform.flip(img, True, False) for img in sonic_right]
sonic_idle  = [sonic_right[0]]
sonic_jump  = [image.load("pics/sonic sprites/sonicjump.png")]

sonic_pics = [sonic_right, sonic_left, sonic_idle, sonic_jump]



coin_pics = add_pics("coins", "coin", 1, 4)

def update_coins(coins):
    for coin in coins:
        coin[4] += 0.15
        if coin[4] >= len(coin_pics):
            coin[4] = 0

def draw_coins(cam, coin_count, lives, coins):
    for coin in coins:
        if not coin[5]:
            frame = transform.scale(coin_pics[int(coin[4])], (coin[2], coin[3]))
            screen.blit(frame, (coin[0] - cam[0], coin[1] - cam[1]))

    f = font.SysFont(None, 36)
    coin_icon = transform.scale(coin_pics[0], (28, 28))
    screen.blit(coin_icon, (10, 10))
    screen.blit(f.render(f"x {coin_count}", True, white), (44, 14))
    screen.blit(f.render(f"LIVES: {lives}", True, white), (10, 50))

def check_coin_collect(p, coin_count, coins):
    player_rect = Rect(p[X], p[Y], p[W], p[H])
    for coin in coins:
        if not coin[5]:
            if player_rect.colliderect(Rect(coin[0], coin[1], coin[2], coin[3])):
                coin[5] = True
                coin_count += 1
    return coin_count

def update_dropped_coins(cam, dropped_coins):
    for dc in dropped_coins:
        dc[6] += 0.15
        if dc[6] >= len(coin_pics):
            dc[6] = 0
            
        dc[0] += dc[4]
        dc[1] += dc[5]
        dc[5] += 0.5 
        
        dummy_p = [dc[0], dc[1], dc[2], dc[3]]
        g_y = get_ground(dummy_p, cam)
        
        if g_y is not None and dc[1] + dc[3] >= g_y - 50:
            dc[1] = g_y - 50 - dc[3]
            dc[5] = -dc[5] * 0.75
            dc[4] *= 0.9
            
        dc[7] -= 1
        
    return [dc for dc in dropped_coins if dc[7] > 0]

def draw_dropped_coins(cam, dropped_coins):
    for dc in dropped_coins:
        frame = transform.scale(coin_pics[int(dc[6])], (dc[2], dc[3]))
        screen.blit(frame, (dc[0] - cam[0], dc[1] - cam[1]))

def collect_dropped_coins(p, coin_count, dropped_coins):
    player_rect = Rect(p[X], p[Y], p[W], p[H])
    
    new_coin_count = coin_count
    for dc in dropped_coins:
        if dc[7] < 160 and player_rect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
            new_coin_count += 1
            
    updated_list = [dc for dc in dropped_coins if not (dc[7] < 160 and player_rect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])))]
    return new_coin_count, updated_list

def update_enemies(cam, enemies):
    for enemy in enemies:
        enemy[0] += enemy[6]
        
        if enemy[0] <= enemy[4] or enemy[0] >= enemy[5]:
            enemy[6] = -enemy[6]
            
        dummy_enemy = [enemy[0], enemy[1], enemy[2], enemy[3]]
        g_y = get_ground(dummy_enemy, cam)
        if g_y is not None:
            enemy[1] = g_y - 50 - enemy[3]

def draw_enemies(cam, enemies):
    for enemy in enemies:
        draw.rect(screen, red, (enemy[0] - cam[0], enemy[1] - cam[1], enemy[2], enemy[3]))

def check_enemy_collision(p, vel, invincibility, coin_count, lives, enemies, dropped_coins):
    if invincibility <= 0:
        player_rect = Rect(p[X], p[Y], p[W], p[H])
        for enemy in enemies:
            enemy_rect = Rect(enemy[0], enemy[1], enemy[2], enemy[3])
            if player_rect.colliderect(enemy_rect):
                vel[1] = -12
                if p[X] < enemy[0]:
                    vel[0] = -10
                else:
                    vel[0] = 10
                    
                invincibility = 120
                
                if coin_count > 0:
                    coins_to_drop = min(coin_count, 20)
                    for i in range(coins_to_drop):
                        angle = random.uniform(0, 2 * pi)
                        speed = random.uniform(4, 9)
                        vx = cos(angle) * speed
                        vy = sin(angle) * speed - 3
                        
                        dropped_coins.append([p[X], p[Y], 32, 32, vx, vy, 0.0, 180])
                    coin_count = 0
                else:
                    lives -= 1
                    p[X], p[Y] = 200, 100
                    vel[0], vel[1] = 0, 0
                    invincibility = 0
                    
    return invincibility, coin_count, lives

def get_ground(p, cam):
    sx = int(p[X] - cam[0] + (p[W] / 2))
    sy = int(p[Y] - cam[1] + p[H])

    if not (0 <= sx < w):
        return None

    for y in range(sy, sy + 300):
        if 0 <= y < h:
            c = screen.get_at((sx, y))[:3]
            if all(abs(c[i] - dirt[i]) <= 15 for i in range(3)):
                return y + cam[1]
        else:
            break
    return None

def update_physics(p, vel, cam, is_jumping, invincibility):
    p[Y] += vel[1]
    ground_y = get_ground(p, cam)
    fall_death = False

    if ground_y is not None:
        if p[Y] + p[H] >= ground_y - 50:
            p[Y] = ground_y - 50 - p[H]
            vel[1] = 0
            is_jumping = False

    if p[Y] > h + 200:
        p[X] = 200
        p[Y] = 100
        vel[0] = 0
        vel[1] = 0
        is_jumping = False
        fall_death = True
        
    if invincibility > 0:
        invincibility -= 1
        
    return is_jumping, invincibility, fall_death

def handle_input(p, vel, is_jumping, invincibility):
    keys = key.get_pressed()

    if invincibility < 100: 
        if (keys[K_SPACE] or keys[K_UP]) and not is_jumping:
            vel[1] = -25
            is_jumping = True

        if keys[K_LEFT]:
            vel[0] -= 0.25 + max(0.05, abs(vel[0]) * 0.02)
        elif keys[K_RIGHT]:
            vel[0] += 0.25 + max(0.05, abs(vel[0]) * 0.02)

    if is_jumping:
        p[ROW] = 3
        p[COL] = 0
    else:
        moving = keys[K_LEFT] or keys[K_RIGHT]
        if keys[K_LEFT]:
            p[ROW] = 1
        elif keys[K_RIGHT]:
            p[ROW] = 0

        if not moving:
            p[ROW] = 2
            p[COL] = 0
        else:
            speed = abs(vel[0])
            p[COL] += 0.1 + speed * 0.03
            num_frames = len(sonic_pics[p[ROW]])
            if p[COL] >= num_frames:
                p[COL] = 0

    if not (keys[K_LEFT] or keys[K_RIGHT]):
        if vel[0] > 0:
            vel[0] -= 0.12 * (1 + abs(vel[0]) * 0.03)
            if vel[0] < 0: vel[0] = 0
        elif vel[0] < 0:
            vel[0] += 0.12 * (1 + abs(vel[0]) * 0.03)
            if vel[0] > 0: vel[0] = 0

    vel[0] = max(-16, min(16, vel[0]))
    p[X] += vel[0]
    vel[1] += 1
    
    return is_jumping

def render(p, cam, coin_count, lives, invincibility, coins, enemies, dropped_coins):
    cam[0] += ((p[X] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[Y] - h // 2) - cam[1]) * 0.08

    screen.blit(bg_img, (-cam[0], -2720 - cam[1]))

    draw_coins(cam, coin_count, lives, coins)
    draw_dropped_coins(cam, dropped_coins)
    draw_enemies(cam, enemies)

    if invincibility % 4 < 2:
        frame = sonic_pics[p[ROW]][int(p[COL])]

        # Scale factor (2.0 = twice original size)
        scale = 3

        orig_w = frame.get_width()
        orig_h = frame.get_height()

        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        frame_scaled = transform.scale(frame, (new_w, new_h))

        draw_x = p[X] - cam[0] - (new_w - p[W]) // 2
        draw_y = p[Y] - cam[1] - (new_h - p[H]) // 2

        screen.blit(frame_scaled, (draw_x, draw_y))

def main_menu():
    c = time.Clock()
    btns = [Rect(100, 100, 200, 50), Rect(100, 200, 200, 50)]
    f = font.SysFont(None, 28)

    while True:
        screen.fill(grey)
        mx, my = mouse.get_pos()

        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == MOUSEBUTTONDOWN and btns[1].collidepoint(mx, my):
                return "play"

        for b in btns:
            draw.rect(screen, blue, b)

        screen.blit(f.render("MENU",    True, white), (160, 110))
        screen.blit(f.render("LEVEL 1", True, white), (130, 210))

        display.flip()
        c.tick(60)

def play_level():
    c = time.Clock()
    p     = [200, 100, 80, 80, 0, 0]
    vel   = [0, 0]
    cam   = [0, 0]
    
    is_jumping = False
    invincibility = 0
    
    coin_count = 0
    lives = 3

    coins = [
        [350, 400, 40, 40, 0.0, False],
    ]
    enemies = [
        [600, 400, 50, 50, 400, 900, 3] 
    ]
    dropped_coins = []

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        if lives <= 0:
            return "menu"

        is_jumping = handle_input(p, vel, is_jumping, invincibility)
        is_jumping, invincibility, fall_death = update_physics(p, vel, cam, is_jumping, invincibility)
        
        if fall_death:
            lives -= 1
        
        update_coins(coins)
        update_enemies(cam, enemies)
        dropped_coins = update_dropped_coins(cam, dropped_coins)
        
        coin_count = check_coin_collect(p, coin_count, coins)
        coin_count, dropped_coins = collect_dropped_coins(p, coin_count, dropped_coins)
        invincibility, coin_count, lives = check_enemy_collision(p, vel, invincibility, coin_count, lives, enemies, dropped_coins)
        
        render(p, cam, coin_count, lives, invincibility, coins, enemies, dropped_coins)

        display.flip()
        c.tick(60)

current = "menu"
while current != "exit":
    if current == "menu":
        current = main_menu()
    elif current == "play":
        current = play_level()

quit()