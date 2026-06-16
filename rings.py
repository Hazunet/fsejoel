from pygame import *
from math import *

init()
w, h = 1200, 900
screen = display.set_mode((w, h))

grey = (127, 127, 127)
blue = (0, 0, 255)
white = (255, 255, 255)
dirt = (109, 36, 0)
yellow = (255, 255, 0)
red = (255, 0, 0)

bg_img = transform.scale(image.load("pics/Sonic BG final.png"), (36720, 4590))

def get_ground(p, cam):
    sx = int(p[0] - cam[0] + (p[2] / 2))
    sy = int(p[1] - cam[1] + p[3])
    
    if sx < 0:
        return None
    elif sx >= w:
        return None
    else:
        for y in range(sy, sy + 300):
            if y < 0:
                break
            elif y >= h:
                break
            else:
                c = screen.get_at((sx, y))[:3]
                d0 = abs(c[0] - dirt[0])
                d1 = abs(c[1] - dirt[1])
                d2 = abs(c[2] - dirt[2])
                if d0 <= 15:
                    if d1 <= 15:
                        if d2 <= 15:
                            return y + cam[1]
        return None

def update_physics(p, vel, cam, stats, ents):
    p[1] += vel[1]
    gy = get_ground(p, cam)
    
    if gy == None:
        pass
    else:
        if p[1] + p[3] >= gy - 50:
            p[1] = gy - 50 - p[3]
            vel[1] = 0
            
    if p[1] > h + 200:
        return "dead"
    else:
        pass
        
    if stats[1] > 0:
        stats[1] -= 1
    else:
        pass
        
    for c in ents[0][:]:
        if p.colliderect(c):
            ents[0].remove(c)
            stats[0] += 1
            
    for e in ents[1]:
        if p.colliderect(e):
            if stats[1] == 0:
                if stats[0] > 0:
                    stats[0] = 0
                    stats[1] = 60
                    if vel[0] > 0:
                        vel[0] = -15
                    else:
                        vel[0] = 15
                    vel[1] = -10
                else:
                    return "dead"
    return "ok"

def handle_input(p, vel, stats):
    k = key.get_pressed()
    
    if k[K_SPACE]:
        if vel[1] == 0:
            vel[1] = -25
    elif k[K_UP]:
        if vel[1] == 0:
            vel[1] = -25
            
    moving = 0
    if stats[1] == 0:
        if k[K_LEFT]:
            vel[0] -= 0.25 + max(0.05, abs(vel[0]) * 0.02)
            moving = 1
        elif k[K_RIGHT]:
            vel[0] += 0.25 + max(0.05, abs(vel[0]) * 0.02)
            moving = 1
            
    if moving == 1:
        pass
    else:
        if vel[0] > 0:
            vel[0] -= 0.12 * (1 + abs(vel[0]) * 0.03)
            if vel[0] < 0:
                vel[0] = 0
        elif vel[0] < 0:
            vel[0] += 0.12 * (1 + abs(vel[0]) * 0.03)
            if vel[0] > 0:
                vel[0] = 0
                
    vel[0] = max(-16, min(16, vel[0]))
    p[0] += vel[0]
    vel[1] += 1

def render(p, cam, stats, ents):
    cam[0] += ((p[0] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[1] - h // 2) - cam[1]) * 0.08
    
    screen.blit(bg_img, (-cam[0], -2720 - cam[1]))
    
    for c in ents[0]:
        draw.rect(screen, yellow, [c[0] - cam[0], c[1] - cam[1], c[2], c[3]])
    for e in ents[1]:
        draw.rect(screen, red, [e[0] - cam[0], e[1] - cam[1], e[2], e[3]])
        
    rem = stats[1] % 8
    if rem < 4:
        draw.rect(screen, blue, [p[0] - cam[0], p[1] - cam[1], p[2], p[3]])
    else:
        pass
        
    f = font.SysFont(None, 36)
    screen.blit(f.render(f"COINS: {stats[0]}", True, white), (20, 20))

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
            elif e.type == MOUSEBUTTONDOWN:
                if btns[1].collidepoint(mx, my):
                    return "play"
        for b in btns:
            draw.rect(screen, blue, b)
        screen.blit(f.render("MENU", True, white), (160, 110))
        screen.blit(f.render("LEVEL 1", True, white), (130, 210))
        display.flip()
        c.tick(60)

def play_level():
    c = time.Clock()
    p = Rect(200, 100, 80, 80)
    vel = [0, 0]
    cam = [0, 0]
    stats = [0, 0] 
    ents = [[Rect(500, 480, 30, 30), Rect(600, 480, 30, 30)], [Rect(800, 460, 50, 50)]]
    
    while True:
        for e in event.get():
            if e.type == QUIT:
                return "menu"
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return "menu"
                    
        handle_input(p, vel, stats)
        res = update_physics(p, vel, cam, stats, ents)
        if res == "dead":
            return "play"
        else:
            pass
        render(p, cam, stats, ents)
        display.flip()
        c.tick(60)

current = "menu"
while current != "exit":
    if current == "menu":
        current = main_menu()
    elif current == "play":
        current = play_level()
        
quit()
