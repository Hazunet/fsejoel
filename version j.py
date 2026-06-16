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
orange = (255, 127, 0)
yellow = (255, 255, 0)

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

SPRITE_W = 110
SPRITE_H = 100

coin_pics = add_pics("coins", "coin", 1, 4)

def update_coins(coins):
    for coin in coins:
        coin[4] += 0.15
        if coin[4] >= len(coin_pics):
            coin[4] = 0

def draw_coins(cam, coin_count, lives, coins):
    for coin in coins:
        if coin[5] == False:
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
        if coin[5] == False:
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
        
        if g_y != None:
            if dc[1] + dc[3] >= g_y - 50:
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
        if dc[7] < 160:
            if player_rect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
                new_coin_count += 1
            
    updated_list = []
    for dc in dropped_coins:
        if dc[7] < 160:
            if player_rect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
                pass
            else:
                updated_list.append(dc)
        else:
            updated_list.append(dc)
            
    return new_coin_count, updated_list

def update_enemies(cam, enemies, p):
    for enemy in enemies:
        dist = sqrt((enemy[0] - p[X])**2 + (enemy[1] - p[Y])**2)
        
        if dist < 350:
            if enemy[4] <= p[X]:
                if p[X] <= enemy[5]:
                    if enemy[0] < p[X]:
                        enemy[6] = abs(enemy[6])
                    else:
                        enemy[6] = -abs(enemy[6])
                    enemy[0] += enemy[6] * 2.5 
                else:
                    enemy[0] += enemy[6]
                    if enemy[0] <= enemy[4]:
                        enemy[0] = enemy[4]
                        enemy[6] = abs(enemy[6])
                    elif enemy[0] >= enemy[5]:
                        enemy[0] = enemy[5]
                        enemy[6] = -abs(enemy[6])
            else:
                enemy[0] += enemy[6]
                if enemy[0] <= enemy[4]:
                    enemy[0] = enemy[4]
                    enemy[6] = abs(enemy[6])
                elif enemy[0] >= enemy[5]:
                    enemy[0] = enemy[5]
                    enemy[6] = -abs(enemy[6])
        else:
            enemy[0] += enemy[6]
            if enemy[0] <= enemy[4]:
                enemy[0] = enemy[4]
                enemy[6] = abs(enemy[6])
            elif enemy[0] >= enemy[5]:
                enemy[0] = enemy[5]
                enemy[6] = -abs(enemy[6])
            
        dummy_enemy = [enemy[0], enemy[1], enemy[2], enemy[3]]
        g_y = get_ground(dummy_enemy, cam)
        if g_y != None:
            enemy[1] = g_y - enemy[3]

def update_fish_enemies(fishes):
    for fish in fishes:
        if fish[4] == False: 
            fish[7] -= 1
            if fish[7] <= 0:
                fish[4] = True
                fish[5] = -20 
        else:
            fish[1] += fish[5]
            fish[5] += 0.6 
            
            if fish[1] >= fish[6]:
                fish[1] = fish[6]
                fish[4] = False
                fish[5] = 0
                fish[7] = 90 

def update_buzz_bombers(bombers, p, projectiles):
    for b in bombers:
        if b[7] > 0:
            b[7] -= 1
        else:
            if b[8] == True:
                b[8] = False
                b[7] = 60
            else:
                b[0] += b[6]
                if b[0] <= b[4]:
                    b[0] = b[4]
                    b[6] = abs(b[6])
                elif b[0] >= b[5]:
                    b[0] = b[5]
                    b[6] = -abs(b[6])

                if abs(p[X] - b[0]) < 250:
                    if p[Y] > b[1]:
                        b[8] = True
                        b[7] = 30
                        if p[X] < b[0]:
                            proj_vx = -5
                        else:
                            proj_vx = 5
                        projectiles.append([b[0] + 20, b[1] + 30, 20, 10, proj_vx, 5])

def update_projectiles(projectiles):
    updated = []
    for pr in projectiles:
        pr[0] += pr[4]
        pr[1] += pr[5]
        if -500 < pr[0]:
            if pr[0] < 40000:
                if pr[1] < h + 500:
                    updated.append(pr)
    return updated

def draw_enemies(cam, enemies, fishes, bombers, projectiles):
    for enemy in enemies:
        draw.rect(screen, red, (enemy[0] - cam[0], enemy[1] - cam[1], enemy[2], enemy[3]))
    for fish in fishes:
        draw.rect(screen, orange, (fish[0] - cam[0], fish[1] - cam[1], fish[2], fish[3]))
    for b in bombers:
        draw.rect(screen, blue, (b[0] - cam[0], b[1] - cam[1], b[2], b[3]))
    for pr in projectiles:
        draw.rect(screen, yellow, (pr[0] - cam[0], pr[1] - cam[1], pr[2], pr[3]))

def check_enemy_collision(p, vel, invincibility, coin_count, lives, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling):
    player_rect = Rect(p[X], p[Y], p[W], p[H])
    
    destroyed_enemies = []
    destroyed_fishes = []
    destroyed_bombers = []
    destroyed_projectiles = []
    
    hit_by_harmful = False
    enemy_x = 0

    for enemy in enemies:
        enemy_rect = Rect(enemy[0], enemy[1], enemy[2], enemy[3])
        if player_rect.colliderect(enemy_rect):
            if is_rolling == True:
                destroyed_enemies.append(enemy)
                vel[1] = -10  
            elif vel[1] > 0:
                destroyed_enemies.append(enemy)
                vel[1] = -10
            else:
                hit_by_harmful = True
                enemy_x = enemy[0]

    for fish in fishes:
        fish_rect = Rect(fish[0], fish[1], fish[2], fish[3])
        if player_rect.colliderect(fish_rect):
            if is_rolling == True:
                destroyed_fishes.append(fish)
                vel[1] = -10
            elif vel[1] > 0:
                destroyed_fishes.append(fish)
                vel[1] = -10
            else:
                hit_by_harmful = True
                enemy_x = fish[0]

    for b in bombers:
        bomber_rect = Rect(b[0], b[1], b[2], b[3])
        if player_rect.colliderect(bomber_rect):
            if is_rolling == True:
                destroyed_bombers.append(b)
                vel[1] = -10
            elif vel[1] > 0:
                destroyed_bombers.append(b)
                vel[1] = -10
            else:
                hit_by_harmful = True
                enemy_x = b[0]

    for pr in projectiles:
        proj_rect = Rect(pr[0], pr[1], pr[2], pr[3])
        if player_rect.colliderect(proj_rect):
            if is_rolling == True:  
                destroyed_projectiles.append(pr)
            else:
                hit_by_harmful = True
                enemy_x = pr[0]

    enemies[:] = [e for e in enemies if e not in destroyed_enemies]
    fishes[:] = [f for f in fishes if f not in destroyed_fishes]
    bombers[:] = [b for b in bombers if b not in destroyed_bombers]
    projectiles[:] = [pr for pr in projectiles if pr not in destroyed_projectiles]

    if hit_by_harmful == True:
        if invincibility <= 0:
            vel[1] = -12
            if p[X] < enemy_x:
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

    if sx < 0:
        return None
    elif sx >= w:
        return None

    for y in range(sy, sy + 300):
        if 0 <= y:
            if y < h:
                c = screen.get_at((sx, y))[:3]
                if abs(c[0] - dirt[0]) <= 15:
                    if abs(c[1] - dirt[1]) <= 15:
                        if abs(c[2] - dirt[2]) <= 15:
                            return y + cam[1]
            else:
                break
        else:
            break
    return None

def update_physics(p, vel, cam, is_jumping, invincibility, is_rolling):
    p[Y] += vel[1]
    ground_y = get_ground(p, cam)
    fall_death = False

    if ground_y != None:
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
        is_rolling = False
        fall_death = True
        
    if invincibility > 0:
        invincibility -= 1
        
    return is_jumping, invincibility, fall_death, is_rolling

def handle_input(p, vel, is_jumping, invincibility, is_rolling, x_pressed_last):
    keys = key.get_pressed()

    if invincibility < 100: 
        if keys[K_SPACE]:
            if is_jumping == False:
                vel[1] = -25
                is_jumping = True
                is_rolling = False
        elif keys[K_UP]:
            if is_jumping == False:
                vel[1] = -25
                is_jumping = True
                is_rolling = False

        if keys[K_x]:
            if x_pressed_last == False:
                x_pressed_last = True
                if is_rolling == True:
                    is_rolling = False
                elif is_jumping == False:
                    is_rolling = True
        else:
            x_pressed_last = False

        if keys[K_LEFT]:
            if is_rolling == True:
                vel[0] -= 0.35  
            else:
                vel[0] -= 0.25 + max(0.05, abs(vel[0]) * 0.02)
        elif keys[K_RIGHT]:
            if is_rolling == True:
                vel[0] += 0.35
            else:
                vel[0] += 0.25 + max(0.05, abs(vel[0]) * 0.02)

    if is_jumping:
        p[ROW] = 3
        p[COL] = 0
    elif is_rolling == False:
        moving = False
        if keys[K_LEFT]:
            moving = True
        elif keys[K_RIGHT]:
            moving = True

        if keys[K_LEFT]:
            p[ROW] = 1
        elif keys[K_RIGHT]:
            p[ROW] = 0

        if moving == False:
            p[ROW] = 2
            p[COL] = 0
        else:
            speed = abs(vel[0])
            p[COL] += 0.1 + speed * 0.03
            num_frames = len(sonic_pics[p[ROW]])
            if p[COL] >= num_frames:
                p[COL] = 0

    if keys[K_LEFT] == False:
        if keys[K_RIGHT] == False:
            if is_rolling == True:
                fric = 0.025  
            else:
                fric = 0.12
                
            if vel[0] > 0:
                vel[0] -= fric * (1 + abs(vel[0]) * 0.03)
                if vel[0] < 0: vel[0] = 0
            elif vel[0] < 0:
                vel[0] += fric * (1 + abs(vel[0]) * 0.03)
                if vel[0] > 0: vel[0] = 0

    if is_rolling == True:
        max_speed = 22
    else:
        max_speed = 16

    vel[0] = max(-max_speed, min(max_speed, vel[0]))
    p[X] += vel[0]
    vel[1] += 1
    
    return is_jumping, is_rolling, x_pressed_last

def render(p, cam, coin_count, lives, invincibility, coins, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling):
    cam[0] += ((p[X] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[Y] - h // 2) - cam[1]) * 0.08

    screen.blit(bg_img, (-cam[0], -2720 - cam[1]))

    draw_coins(cam, coin_count, lives, coins)
    draw_dropped_coins(cam, dropped_coins)
    draw_enemies(cam, enemies, fishes, bombers, projectiles)

    if invincibility % 4 < 2:
        if is_rolling == True:
            draw_x = int(p[X] - cam[0] + p[W] // 2)
            draw_y = int(p[Y] - cam[1] + p[H] // 2)
            radius = int(p[W] // 2)
            draw.circle(screen, blue, (draw_x, draw_y), radius)
            draw.circle(screen, white, (draw_x, draw_y), radius - 10, 3) 
        else:
            frame = sonic_pics[p[ROW]][int(p[COL])]
            frame_scaled = transform.scale(frame, (SPRITE_W, SPRITE_H))
            draw_x = p[X] - cam[0] - (SPRITE_W - p[W]) // 2
            draw_y = p[Y] - cam[1] - (SPRITE_H - p[H]) // 2
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
            if e.type == MOUSEBUTTONDOWN:
                if btns[1].collidepoint(mx, my):
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
    is_rolling = False
    x_pressed_last = False
    invincibility = 0
    
    coin_count = 0
    lives = 3

    coins = [
        [350, 400, 40, 40, 0.0, False],
        [1000, 400, 40, 40, 0.0, False],
        [1060, 400, 40, 40, 0.0, False],
    ]
    
    enemies = [
        [600, 400, 50, 50, 400, 900, 3] 
    ]
    
    fishes = [
        [450, 650, 45, 45, False, 0.0, 650, 60]
    ]

    bombers = [
        [1400, 250, 60, 40, 1100, 1700, 2, 0, False]
    ]
    projectiles = []
    
    dropped_coins = []

    while True:
        for e in event.get():
            if e.type == QUIT:
                return "menu"
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return "menu"

        if lives <= 0:
            return "menu"

        is_jumping, is_rolling, x_pressed_last = handle_input(p, vel, is_jumping, invincibility, is_rolling, x_pressed_last)
        is_jumping, invincibility, fall_death, is_rolling = update_physics(p, vel, cam, is_jumping, invincibility, is_rolling)
        
        if fall_death == True:
            lives -= 1
        
        update_coins(coins)
        update_enemies(cam, enemies, p)
        update_fish_enemies(fishes)
        update_buzz_bombers(bombers, p, projectiles)
        projectiles = update_projectiles(projectiles)
        dropped_coins = update_dropped_coins(cam, dropped_coins)
        
        coin_count = check_coin_collect(p, coin_count, coins)
        coin_count, dropped_coins = collect_dropped_coins(p, coin_count, dropped_coins)
        invincibility, coin_count, lives = check_enemy_collision(
            p, vel, invincibility, coin_count, lives, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling
        )
        
        render(p, cam, coin_count, lives, invincibility, coins, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling)

        display.flip()
        c.tick(60)

current = "menu"
while current != "exit":
    if current == "menu":
        current = main_menu()
    elif current == "play":
        current = play_level()

quit()