import pygame
from pygame import *

pygame.init()
width, height = 800, 500
screen = display.set_mode((width, height))
display.set_caption("Colour Detection Demo")

sky    = (135, 206, 235)
blue   = (30, 100, 200)
yellow = (255, 215, 0)
white  = (255, 255, 255)
black  = (0, 0, 0)

DIRT_COLOUR = (36, 0, 0)
HOVER_OFFSET = 50       # how many pixels above the dirt the player hovers
SCAN_DEPTH   = 200      # how many pixels below feet we scan downward
TOLERANCE    = 10       # how close the colour needs to be (for compression artifacts)

gravity   = 0.7
jumpPower = -15

player = {
    'x': 80.0, 'y': 100.0,
    'w': 30, 'h': 30,
    'vx': 0.0, 'vy': 0.0,
    'on_ground': False,
}

# load your actual background here instead
# bg = image.load("pics/Sonic BG final.png")
# bg = transform.scale(bg, (36720, 4590))
# for now we draw a fake background with dirt colour to prove the concept

def draw_fake_bg():
    screen.fill(sky)
    # fake ground with the exact dirt colour
    draw.rect(screen, (36, 0, 0), (0, 350, 800, 150))
    # fake raised platform with dirt colour
    draw.rect(screen, (36, 0, 0), (200, 260, 200, 30))
    draw.rect(screen, (36, 0, 0), (500, 220, 180, 30))
    # green top strips so it looks like a platform
    draw.rect(screen, (76,175,80), (0,   350, 800, 8))
    draw.rect(screen, (76,175,80), (200, 260, 200, 8))
    draw.rect(screen, (76,175,80), (500, 220, 180, 8))

def colour_close(c1, c2, tol):
    return all(abs(c1[i]-c2[i]) <= tol for i in range(3))

def find_ground_below(px, py, pw):
    """Scan downward from feet center, return Y of first dirt pixel or None."""
    feet_y = int(py + pw)   # using pw as h since square
    mid_x  = int(px + pw / 2)
    mid_x  = max(0, min(width - 1, mid_x))

    for scan_y in range(feet_y, min(feet_y + SCAN_DEPTH, height)):
        try:
            col = screen.get_at((mid_x, scan_y))[:3]
        except:
            break
        if colour_close(col, DIRT_COLOUR, TOLERANCE):
            return scan_y
    return None

def check(p):
    p['on_ground'] = False

    if p['vy'] < 0:      # jumping upward, skip ground check
        p['y'] += p['vy']
        p['vy'] += gravity
        return

    ground_y = find_ground_below(p['x'], p['y'], p['w'])

    if ground_y is not None:
        target_y = ground_y - HOVER_OFFSET - p['h']
        feet = p['y'] + p['h']
        # if player is at or below where they should hover, snap up
        if feet >= ground_y - HOVER_OFFSET:
            p['y'] = target_y
            p['vy'] = 0
            p['on_ground'] = True
        else:
            # still falling toward ground
            p['y'] += p['vy']
            p['vy'] += gravity
    else:
        # no ground found, just fall
        p['y'] += p['vy']
        p['vy'] += gravity

def move(p):
    keys = key.get_pressed()

    if (keys[K_SPACE] or keys[K_UP] or keys[K_w]) and p['on_ground']:
        p['vy'] = jumpPower
        p['on_ground'] = False

    p['vx'] = 0
    if keys[K_LEFT]  or keys[K_a]: p['vx'] = -5
    if keys[K_RIGHT] or keys[K_d]: p['vx'] =  5

    p['x'] += p['vx']

    if p['x'] < 0: p['x'] = 0
    if p['x'] + p['w'] > width: p['x'] = width - p['w']
    if p['y'] > height + 50:
        p['x'], p['y'] = 80, 100
        p['vx'], p['vy'] = 0, 0

def draw_player(surf, p):
    x, y, w, h = int(p['x']), int(p['y']), p['w'], p['h']
    draw.rect(surf, blue,   (x, y, w, h))
    draw.rect(surf, yellow, (x, y, w, 8))
    draw.circle(surf, white, (x+w-8, y+8), 5)
    draw.circle(surf, black, (x+w-8, y+8), 2)

clock = time.Clock()
running = True
while running:
    for evt in event.get():
        if evt.type == QUIT: running = False
        if evt.type == KEYDOWN and evt.key == K_ESCAPE: running = False

    # IMPORTANT: background must be drawn BEFORE check() so screen.get_at reads correct pixels
    draw_fake_bg()

    check(player)
    move(player)
    draw_player(screen, player)

    font = pygame.font.SysFont(None, 20)
    screen.blit(font.render("Arrow keys / WASD   ·   Space to jump", True, black), (10, 10))
    screen.blit(font.render(f"scanning pixel at ({int(player['x']+player['w']//2)}, {int(player['y']+player['h'])})", True, black), (10, 30))

    display.flip()
    clock.tick(60)

pygame.quit()