import pygame
from pygame import *
from math import tan, radians, cos, sin

pygame.init()
width, height = 800, 500
screen = display.set_mode((width, height))
display.set_caption("Slope Tilt Demo")

blue   = (30, 100, 200)
brown  = (93, 64, 55)
green  = (76, 175, 80)
sky    = (135, 206, 235)
yellow = (255, 215, 0)
white  = (255, 255, 255)
black  = (0, 0, 0)

gravity   = 0.7
jumpPower = -15

# (x, y, w, h, angle_degrees)
platforms = [
    (0,   420, 200, 20,   0),
    (200, 408,  80, 12,  -9),
    (280, 390,  80, 12, -13),
    (360, 365,  80, 12, -17),
    (440, 355, 160, 20,   0),
    (600, 365,  80, 12,  13),
    (680, 385, 120, 20,   0),
    (0,   480, 800, 20,   0),
]

player = {
    'x': 50.0, 'y': 370.0,
    'w': 30, 'h': 30,
    'vx': 0.0, 'vy': 0.0,
    'angle': 0.0,
    'on_ground': False,
}

SNAP_DIST = 12  # how many pixels below surface we still snap up

def get_surface_y(plat, px):
    x, y, w, h, angle = plat
    rel_x = max(0, min(w, px - x))  # clamp within platform width
    return y + tan(radians(angle)) * rel_x

def check(p, plats):
    p['on_ground'] = False
    p['angle'] = 0.0
    feet = p['y'] + p['h']
    mid_x = p['x'] + p['w'] / 2

    for plat in plats:
        px, py, pw, ph, angle = plat

        # horizontal overlap
        if p['x'] + p['w'] <= px or p['x'] >= px + pw:
            continue

        surf_y = get_surface_y(plat, mid_x)

        # snap if feet are within SNAP_DIST below surface AND moving down or standing
        # this catches both: walking onto a slope horizontally, and falling onto it
        if feet <= surf_y + SNAP_DIST and feet >= surf_y - 2:
            if p['vy'] >= 0:  # only snap when not jumping upward
                p['vy'] = 0
                p['y'] = surf_y - p['h']
                p['on_ground'] = True
                p['angle'] = angle

    p['y'] += p['vy']

def move(p):
    keys = key.get_pressed()

    if (keys[K_SPACE] or keys[K_UP] or keys[K_w]) and p['on_ground']:
        p['vy'] = jumpPower
        p['on_ground'] = False

    p['vx'] = 0
    if keys[K_LEFT]  or keys[K_a]: p['vx'] = -5
    if keys[K_RIGHT] or keys[K_d]: p['vx'] =  5

    p['x'] += p['vx']
    p['vy'] += gravity

    if p['x'] < 0: p['x'] = 0
    if p['x'] + p['w'] > width: p['x'] = width - p['w']
    if p['y'] > height + 50:
        p['x'], p['y'] = 50, 370
        p['vx'], p['vy'] = 0, 0

def draw_platform(surf, plat):
    px, py, pw, ph, angle = plat
    cx, cy = px + pw / 2, py + ph / 2
    a = radians(angle)
    def rot(lx, ly):
        return (cx + lx*cos(a) - ly*sin(a),
                cy + lx*sin(a) + ly*cos(a))
    pts = [rot(-pw/2,-ph/2), rot(pw/2,-ph/2), rot(pw/2,ph/2), rot(-pw/2,ph/2)]
    draw.polygon(surf, brown, pts)
    top = [rot(-pw/2,-ph/2), rot(pw/2,-ph/2), rot(pw/2,-ph/2+6), rot(-pw/2,-ph/2+6)]
    draw.polygon(surf, green, top)

def draw_player(surf, p):
    cx = p['x'] + p['w'] / 2
    cy = p['y'] + p['h'] / 2
    a  = radians(p['angle'])
    def rot(lx, ly):
        return (int(cx + lx*cos(a) - ly*sin(a)),
                int(cy + lx*sin(a) + ly*cos(a)))
    hw, hh = p['w']/2, p['h']/2
    draw.polygon(surf, blue,   [rot(-hw,-hh),rot(hw,-hh),rot(hw,hh),rot(-hw,hh)])
    draw.polygon(surf, yellow, [rot(-hw,-hh),rot(hw,-hh),rot(hw,-hh+8),rot(-hw,-hh+8)])
    ex, ey = rot(5, -6)
    draw.circle(surf, white, (ex,ey), 5)
    draw.circle(surf, black, (ex,ey), 2)
    if p['on_ground'] and abs(p['angle']) > 1:
        font = pygame.font.SysFont(None, 22)
        surf.blit(font.render(f"tilt: {p['angle']:.0f}°", True, black), (10,10))

clock = time.Clock()
running = True
while running:
    for evt in event.get():
        if evt.type == QUIT: running = False
        if evt.type == KEYDOWN and evt.key == K_ESCAPE: running = False

    screen.fill(sky)
    check(player, platforms)
    move(player)
    for plat in platforms:
        draw_platform(screen, plat)
    draw_player(screen, player)
    font = pygame.font.SysFont(None, 20)
    screen.blit(font.render("Arrow keys / WASD to move   ·   Space or Up to jump", True, (50,50,50)),
                (width//2 - 210, height-28))
    display.flip()
    clock.tick(60)

pygame.quit()