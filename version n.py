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
light_blue = (0, 191, 255) 

X = 0
Y = 1
W = 2
H = 3
ROW = 4
COL = 5

SPRITE_W = 110
SPRITE_H = 100

bg_img = transform.scale(image.load("pics/Sonic BG final.png"), (36720, 4590))

def add_pics(folder, name, start, end):
    pics = []
    for i in range(start, end):
        pics.append(image.load(f"pics/{folder}/{name}{i}.png"))
    return pics

# Standard Sonic Animations
sonic_right = add_pics("sonic sprites", "sonic", 1, 10)
sonic_left  = [transform.flip(img, True, False) for img in sonic_right]
sonic_idle  = [sonic_right[0]]
sonic_jump  = [image.load("pics/sonic sprites/sonicjump.png")]

# Roll & Slide Animations
sonic_roll_start = add_pics("sonic sprites", "sonicroll", 1, 6) 
sonic_ball_loop  = [image.load("pics/sonic sprites/mainsonicroll.png")]
sonic_slide      = add_pics("sonic sprites", "sonicslide", 1, 3) 

sonic_pics = [sonic_right, sonic_left, sonic_idle, sonic_jump, sonic_slide]

coin_pics = add_pics("coins", "coin", 1, 4)
fish_pics = add_pics("fish", "fish", 1, 3)
crab_pics = add_pics("crab", "crab", 1, 5)
jump_pics = add_pics("jump", "jump", 1, 3)

# Powerup Sprites Loading
monitor_active_img = image.load("pics/powerup/powerup1.png")
monitor_broken_img = image.load("pics/powerup/powerup2.png")
ability_item_img   = image.load("pics/powerup/ability.png")

# Buzz Bomber Sprites Loading
buzz_flight_pics = add_pics("buzzbomber", "buzz", 1, 6)
buzz_shot_pic    = image.load("pics/buzzbomber/buzzshot.png")

def update_coins(coins):
    for coin in coins:
        coin[4] += 0.15
        if coin[4] >= len(coin_pics):
            coin[4] = 0

def draw_hud(cam, coin_count, lives, coins, elapsed_time, power_timer):
    for coin in coins:
        if coin[5] == False:
            frame = transform.scale(coin_pics[int(coin[4])], (coin[2], coin[3]))
            screen.blit(frame, (coin[0] - cam[0], coin[1] - cam[1]))

    f = font.SysFont(None, 36)
    coin_icon = transform.scale(coin_pics[0], (28, 28))
    screen.blit(coin_icon, (10, 10))
    screen.blit(f.render(f"x {coin_count}", True, white), (44, 14))
    screen.blit(f.render(f"LIVES: {lives}", True, white), (10, 50))
    
    seconds = int(elapsed_time % 60)
    minutes = int(elapsed_time // 60)
    sec_str = f"0{seconds}" if seconds < 10 else f"{seconds}"
    screen.blit(f.render(f"TIME: {minutes}:{sec_str}", True, white), (10, 90))

    if power_timer > 0:
        p_secs = int((power_timer / 60) + 1)
        screen.blit(f.render(f"INVINCIBLE: {p_secs}s", True, yellow), (10, 130))

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
        enemy[7] += 0.15
        if enemy[7] >= len(crab_pics):
            enemy[7] = 0.0

        dist = sqrt((enemy[0] - p[X])**2 + (enemy[1] - p[Y])**2)
        
        if dist < 350:
            if enemy[0] < p[X]:
                enemy[6] = abs(enemy[6]) 
                enemy[0] += 2.5          
            else:
                enemy[6] = -abs(enemy[6]) 
                enemy[0] -= 2.5           
        else:
            enemy[0] += enemy[6]
            if enemy[0] <= enemy[4]:
                enemy[0] = enemy[4]
                enemy[6] = abs(enemy[6])
            elif enemy[0] >= enemy[5]:
                enemy[0] = enemy[5]
                enemy[6] = -abs(enemy[6])

def update_fish_enemies(fishes):
    for fish in fishes:
        fish[8] += 0.15
        if fish[8] >= len(fish_pics):
            fish[8] = 0

        if fish[4] == False: 
            fish[7] -= 1
            if fish[7] <= 0:
                fish[4] = True
                fish[5] = -14 
        else:
            fish[1] += fish[5]
            fish[5] += 0.3 
            
            if fish[1] >= fish[6]:
                fish[1] = fish[6]
                fish[4] = False
                fish[5] = 0
                fish[7] = 60 

def update_buzz_bombers(bombers, p, projectiles):
    # b array values: [X, Y, W, H, MinX, MaxX, Vx, ShootTimer, IsShooting, FrameIdx]
    for b in bombers:
        b[9] += 0.20  # Progress flight cycle animation frame
        if b[9] >= len(buzz_flight_pics):
            b[9] = 0.0

        if b[8] == True:  # Is currently planning/charging a shot
            if b[7] > 0:
                b[7] -= 1
                if b[7] == 0:  # Exactly 1 second delay has run out, fire weapon
                    if p[X] < b[0]:
                        proj_vx = -5
                        b[6] = -abs(b[6]) # Ensure facing direction faces target
                    else:
                        proj_vx = 5
                        b[6] = abs(b[6])
                    projectiles.append([b[0] + 20, b[1] + 40, 20, 10, proj_vx, 5])
            else:
                # Add post-shot cooldown recovery state before resuming movement
                b[8] = False
                b[7] = 120  # Set raw frame countdown until allowed to target fire again
        else:
            if b[7] > 0:
                b[7] -= 1  # Track firing loop cooldown behavior timer

            # Move bomber horizontally during patrol loop
            b[0] += b[6]
            if b[0] <= b[4]:
                b[0] = b[4]
                b[6] = abs(b[6])
            elif b[0] >= b[5]:
                b[0] = b[5]
                b[6] = -abs(b[6])

            # Trigger lock-on condition check if target is inside immediate combat vision zone
            if b[7] <= 0 and abs(p[X] - b[0]) < 300 and p[Y] > b[1]:
                b[8] = True
                b[7] = 60  # Wait exactly 1 second (60 frames) tracking in buzzshot state before firing

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

def draw_enemies(cam, enemies, fishes, bombers, projectiles, win_box, jump_pad, monitor, star):
    draw.rect(screen, yellow, (win_box[0] - cam[0], win_box[1] - cam[1], win_box[2], win_box[3]))
    
    if jump_pad[4] == True:
        frame = jump_pics[1] 
    else:
        frame = jump_pics[0] 
        
    frame_scaled = transform.scale(frame, (jump_pad[2], jump_pad[3]))
    screen.blit(frame_scaled, (jump_pad[0] - cam[0], jump_pad[1] - cam[1]))
    
    if monitor[4] == False:
        m_frame = transform.scale(monitor_active_img, (monitor[2], monitor[3]))
        screen.blit(m_frame, (monitor[0] - cam[0], monitor[1] - cam[1]))
    else:
        broken_w = monitor[2]
        broken_h = monitor[3] // 2
        m_frame = transform.scale(monitor_broken_img, (broken_w, broken_h))
        screen.blit(m_frame, (monitor[0] - cam[0], monitor[1] + broken_h - cam[1]))
        
    if star[2] == True:
        ability_scaled = transform.scale(ability_item_img, (60, 60))
        screen.blit(ability_scaled, (int(star[0] - cam[0] - 30), int(star[1] - cam[1] - 30)))
    
    for enemy in enemies:
        frame = crab_pics[int(enemy[7])]
        frame_scaled = transform.scale(frame, (enemy[2], enemy[3]))
        if enemy[6] < 0:
            frame_scaled = transform.flip(frame_scaled, True, False)
        screen.blit(frame_scaled, (enemy[0] - cam[0], enemy[1] - cam[1]))
        
    for fish in fishes:
        frame = fish_pics[int(fish[8])]
        frame_scaled = transform.scale(frame, (fish[2], fish[3]))
        if fish[5] > 0:
            frame_scaled = transform.flip(frame_scaled, False, True)
        screen.blit(frame_scaled, (fish[0] - cam[0], fish[1] - cam[1]))
        
    # Render Buzz Bomber Animations
    for b in bombers:
        if b[8] == True:
            # Display target preparation layout frame sprite
            b_frame = buzz_shot_pic
        else:
            # Cycle through active wing loops index
            b_frame = buzz_flight_pics[int(b[9])]
            
        b_scaled = transform.scale(b_frame, (b[2], b[3]))
        # Flip asset alignment depending on horizontal velocity heading direction
        if b[6] > 0:
            b_scaled = transform.flip(b_scaled, True, False)
            
        screen.blit(b_scaled, (b[0] - cam[0], b[1] - cam[1]))

    for pr in projectiles:
        draw.rect(screen, yellow, (pr[0] - cam[0], pr[1] - cam[1], pr[2], pr[3]))

def check_enemy_collision(p, vel, invincibility, coin_count, lives, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling, god_mode):
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
            if is_rolling == True or god_mode:
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
            if is_rolling == True or god_mode:
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
            if is_rolling == True or god_mode:
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
            if is_rolling == True or god_mode:  
                destroyed_projectiles.append(pr)
            else:
                hit_by_harmful = True
                enemy_x = pr[0]

    enemies[:] = [e for e in enemies if e not in destroyed_enemies]
    fishes[:] = [f for f in fishes if f not in destroyed_fishes]
    bombers[:] = [b for b in bombers if b not in destroyed_bombers]
    projectiles[:] = [pr for pr in projectiles if pr not in destroyed_projectiles]

    if hit_by_harmful == True and not god_mode:
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
                p[X], p[Y] = 200, 425
                vel[0], vel[1] = 0, 0
                invincibility = 0
            
    return invincibility, coin_count, lives

def get_ground(p, cam):
    sx = int(p[X] - cam[0] + (p[W] / 2))
    sy = int(p[Y] - cam[1] + p[H])

    if sx < 0 or sx >= w:
        return None

    for y in range(sy, sy + 300):
        if 0 <= y < h:
            c = screen.get_at((sx, y))[:3]
            if abs(c[0] - dirt[0]) <= 15 and abs(c[1] - dirt[1]) <= 15 and abs(c[2] - dirt[2]) <= 15:
                return y + cam[1]
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
        p[Y] = 425
        vel[0] = 0
        vel[1] = 0
        is_jumping = False
        is_rolling = False
        fall_death = True
        
    if invincibility > 0:
        invincibility -= 1
        
    return is_jumping, invincibility, fall_death, is_rolling

def handle_input(p, vel, is_jumping, invincibility, is_rolling, roll_frame):
    keys = key.get_pressed()

    if invincibility < 100 or True: 
        if keys[K_SPACE] or keys[K_UP]:
            if is_jumping == False:
                vel[1] = -25
                is_jumping = True

        if keys[K_x]:
            if is_rolling == False:
                is_rolling = True
                roll_frame = 0.0  
        else:
            is_rolling = False  

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

    if is_rolling:
        speed = abs(vel[0])
        roll_frame += 0.2 + speed * 0.02
    elif is_jumping:
        p[ROW] = 3
        p[COL] = 0
    else:
        moving = False
        if keys[K_LEFT] or keys[K_RIGHT]:
            moving = True

        if moving == False and abs(vel[0]) > 6.0:
            p[ROW] = 4  
            p[COL] += 0.15
            if p[COL] >= len(sonic_pics[4]):
                p[COL] = 0
        else:
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

    if keys[K_LEFT] == False and keys[K_RIGHT] == False:
        fric = 0.025 if is_rolling else 0.12
        if vel[0] > 0:
            vel[0] -= fric * (1 + abs(vel[0]) * 0.03)
            if vel[0] < 0: vel[0] = 0
        elif vel[0] < 0:
            vel[0] += fric * (1 + abs(vel[0]) * 0.03)
            if vel[0] > 0: vel[0] = 0

    max_speed = 22 if is_rolling else 16

    vel[0] = max(-max_speed, min(max_speed, vel[0]))
    p[X] += vel[0]
    vel[1] += 1
    
    return is_jumping, is_rolling, roll_frame

def render(p, cam, coin_count, lives, invincibility, coins, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling, elapsed_time, win_box, jump_pad, monitor, star, power_timer, roll_frame, vel):
    cam[0] += ((p[X] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[Y] - h // 2) - cam[1]) * 0.08

    screen.blit(bg_img, (-cam[0], -2720 - cam[1]))

    draw_hud(cam, coin_count, lives, coins, elapsed_time, power_timer)
    draw_dropped_coins(cam, dropped_coins)
    draw_enemies(cam, enemies, fishes, bombers, projectiles, win_box, jump_pad, monitor, star)

    god_mode = power_timer > 0
    
    should_draw = True
    if not god_mode:
        if invincibility > 0:
            if invincibility % 4 >= 2:
                should_draw = False

    if should_draw:
        if is_rolling == True:
            if roll_frame < 5:
                frame = sonic_roll_start[int(roll_frame)]
            else:
                frame = sonic_ball_loop[0] 

            if vel[0] < 0:
                frame = transform.flip(frame, True, False)

            frame_scaled = transform.scale(frame, (SPRITE_W, SPRITE_H))
            
            if god_mode and (power_timer % 4 < 2):
                tint_surf = Surface((SPRITE_W, SPRITE_H), SRCALPHA)
                tint_surf.fill((255, 255, 0, 140)) 
                frame_scaled = frame_scaled.copy()
                frame_scaled.blit(tint_surf, (0, 0), special_flags=BLEND_RGBA_MULT)

            draw_x = p[X] - cam[0] - (SPRITE_W - p[W]) // 2
            draw_y = p[Y] - cam[1] - (SPRITE_H - p[H]) // 2
            screen.blit(frame_scaled, (draw_x, draw_y))
        else:
            frame = sonic_pics[p[ROW]][int(p[COL])]
            frame_scaled = transform.scale(frame, (SPRITE_W, SPRITE_H))
            
            if (p[ROW] == 4 or p[ROW] == 3) and vel[0] < 0:
                frame_scaled = transform.flip(frame_scaled, True, False)
            
            if god_mode and (power_timer % 4 < 2):
                tint_surf = Surface((SPRITE_W, SPRITE_H), SRCALPHA)
                tint_surf.fill((255, 255, 0, 140)) 
                frame_scaled = frame_scaled.copy()
                frame_scaled.blit(tint_surf, (0, 0), special_flags=BLEND_RGBA_MULT)

            draw_x = p[X] - cam[0] - (SPRITE_W - p[W]) // 2
            draw_y = p[Y] - cam[1] - (SPRITE_H - p[H]) // 2
            screen.blit(frame_scaled, (draw_x, draw_y))
            
            if god_mode:
                draw.circle(screen, white, (int(p[X] - cam[0] + random.randint(0, p[W])), int(p[Y] - cam[1] - 10)), 5)

def draw_victory_screen(elapsed_time):
    f_large = font.SysFont(None, 72)
    f_small = font.SysFont(None, 48)
    
    seconds = int(elapsed_time % 60)
    minutes = int(elapsed_time // 60)
    sec_str = f"0{seconds}" if seconds < 10 else f"{seconds}"

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        overlay = Surface((w, h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(10)
        screen.blit(overlay, (0, 0))

        txt_win = f_large.render("YOU WON!", True, yellow)
        txt_time = f_small.render(f"Final Time: {minutes}:{sec_str}", True, white)
        txt_exit = f_small.render("Press ESC to return to Menu", True, grey)

        screen.blit(txt_win, (w // 2 - txt_win.get_width() // 2, h // 2 - 100))
        screen.blit(txt_time, (w // 2 - txt_time.get_width() // 2, h // 2))
        screen.blit(txt_exit, (w // 2 - txt_exit.get_width() // 2, h // 2 + 100))

        display.flip()

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
    p     = [200, 425, 80, 80, 0, 0] 
    vel   = [0, 0]
    cam   = [0, 0]
    
    is_jumping = False
    is_rolling = False
    roll_frame = 0.0 
    invincibility = 0
    power_timer = 0 
    
    coin_count = 0
    lives = 3
    elapsed_time = 0.0

    coins = [
        [350, 400, 40, 40, 0.0, False],
        [1000, 400, 40, 40, 0.0, False],
        [1060, 400, 40, 40, 0.0, False],
    ]
    
    enemies = [
        [600, 405, 140, 100, 400, 1000, 2, 0.0] 
    ]
    
    fishes = [
        [450, 650, 100, 100, False, 0.0, 650, 60, 0.0]
    ]

    # Added structural value b[9] for counting flight frame animation loop indexing
    # Form: [X, Y, W, H, MinPatrolX, MaxPatrolX, Vx, TimerState, IsShooting, FrameIndexValue]
    bombers = [
        [1400, 250, 110, 80, 1100, 2200, 2.5, 0, False, 0.0]
    ]
    projectiles = []
    dropped_coins = []
    
    win_box = [2600, 350, 100, 100] 
    jump_pad = [500, 425, 120, 80, False, 0]
    
    monitor = [1800, 340, 120, 120, False]
    star = [0.0, 0.0, False, 0.0]

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        if lives <= 0:
            return "menu"

        elapsed_time += 1.0 / 60.0
        if power_timer > 0:
            power_timer -= 1

        god_mode = power_timer > 0

        is_jumping, is_rolling, roll_frame = handle_input(p, vel, is_jumping, invincibility, is_rolling, roll_frame)
        is_jumping, invincibility, fall_death, is_rolling = update_physics(p, vel, cam, is_jumping, invincibility, is_rolling)
        
        if fall_death == True:
            lives -= 1
            power_timer = 0
            p[Y] = 425  
        
        update_coins(coins)
        update_enemies(cam, enemies, p)
        update_fish_enemies(fishes)
        update_buzz_bombers(bombers, p, projectiles)
        projectiles = update_projectiles(projectiles)
        dropped_coins = update_dropped_coins(cam, dropped_coins)
        
        coin_count = check_coin_collect(p, coin_count, coins)
        coin_count, dropped_coins = collect_dropped_coins(p, coin_count, dropped_coins)
        invincibility, coin_count, lives = check_enemy_collision(
            p, vel, invincibility, coin_count, lives, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling, god_mode
        )
        
        player_rect = Rect(p[X], p[Y], p[W], p[H])
        
        if jump_pad[4] == True:
            jump_pad[5] -= 1
            if jump_pad[5] <= 0:
                jump_pad[4] = False

        if player_rect.colliderect(Rect(jump_pad[0], jump_pad[1], jump_pad[2], jump_pad[3])):
            vel[1] = -32          
            is_jumping = True     
            p[ROW] = 3            
            p[COL] = 0
            
            jump_pad[4] = True
            jump_pad[5] = 15 

        if monitor[4] == False:
            if player_rect.colliderect(Rect(monitor[0], monitor[1], monitor[2], monitor[3])):
                monitor[4] = True 
                star[0] = monitor[0] + 60 
                star[1] = monitor[1] + 30
                star[2] = True 
                star[3] = monitor[1] - 80 
                
        if star[2] == True:
            if star[1] > star[3]:
                star[1] -= 2.0

        if star[2] == True:
            star_dist = sqrt((p[X] + p[W]//2 - star[0])**2 + (p[Y] + p[H]//2 - star[1])**2)
            if star_dist < 65: 
                star[2] = False
                power_timer = 1200 

        if player_rect.colliderect(Rect(win_box[0], win_box[1], win_box[2], win_box[3])):
            return draw_victory_screen(elapsed_time)
        
        render(p, cam, coin_count, lives, invincibility, coins, enemies, fishes, bombers, projectiles, dropped_coins, is_rolling, elapsed_time, win_box, jump_pad, monitor, star, power_timer, roll_frame, vel)

        display.flip()
        c.tick(60)

current = "menu"
while current != "exit":
    if current == "menu":
        current = main_menu()
    elif current == "play":
        current = play_level()

quit()