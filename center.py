from pygame import *
from math import *

init()
w, h = 1200, 900
screen = display.set_mode((w, h))

grey = (127, 127, 127)
blue = (0, 0, 255)
white = (255, 255, 255)
dirt = (109, 36, 0)

bg_img = transform.scale(image.load("pics/Sonic BG final.png"), (36720, 4590))

def get_ground(p, cam):
    sx = int(p[0] - cam[0] + (p[2] / 2))
    sy = int(p[1] - cam[1] + p[3])
    
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

def update_physics(p, vel, cam):
    p[1] += vel[1]
    ground_y = get_ground(p, cam)
    
    if ground_y is not None:
        if p[1] + p[3] >= ground_y - 50:
            p[1] = ground_y - 50 - p[3]
            vel[1] = 0
            
    if p[1] > h + 200:
        p[0] = 200
        p[1] = 100
        vel[0] = 0
        vel[1] = 0

def handle_input(p, vel):
    keys = key.get_pressed()
    
    if (keys[K_SPACE] or keys[K_UP]) and vel[1] == 0:
        vel[1] = -25
        
    moving = False
    if keys[K_LEFT]:
        vel[0] -= 0.25 + max(0.05, abs(vel[0]) * 0.02)
        moving = True
    elif keys[K_RIGHT]:
        vel[0] += 0.25 + max(0.05, abs(vel[0]) * 0.02)
        moving = True
        
    if not moving:
        if vel[0] > 0:
            vel[0] -= 0.12 * (1 + abs(vel[0]) * 0.03)
            if vel[0] < 0: vel[0] = 0
        elif vel[0] < 0:
            vel[0] += 0.12 * (1 + abs(vel[0]) * 0.03)
            if vel[0] > 0: vel[0] = 0
            
    vel[0] = max(-16, min(16, vel[0]))
    p[0] += vel[0]
    vel[1] += 1

def render(p, cam):
    cam[0] += ((p[0] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[1] - h // 2) - cam[1]) * 0.08
    
    screen.blit(bg_img, (-cam[0], -2720 - cam[1]))
    draw.rect(screen, blue, [p[0] - cam[0], p[1] - cam[1], p[2], p[3]])

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
            
        screen.blit(f.render("MENU", True, white), (160, 110))
        screen.blit(f.render("LEVEL 1", True, white), (130, 210))
        
        display.flip()
        c.tick(60)

def play_level():
    c = time.Clock()
    p = Rect(200, 100, 80, 80)
    vel = [0, 0]
    cam = [0, 0]
    
    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"
                
        handle_input(p, vel)
        update_physics(p, vel, cam)
        render(p, cam)
        
        display.flip()
        c.tick(60)

current = "menu"
while current != "exit":
    if current == "menu":
        current = main_menu()
    elif current == "play":
        current = play_level()
        
quit()