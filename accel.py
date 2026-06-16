#FSE By BW & JL
#Sonic The Hedgehog: Green Hill Zone

from pygame import *
from math import *

init()
width,height=1200,900
screen=display.set_mode((width,height))

#Colours
grey=(127,127,127)
black=(0,0,0)
blue=(0,0,255)
white=(255,255,255)


gravity=1
X=0
Y=1
rW=2
grndLv=2
rH=3

vel=[0,0,0,0]
jumpPower=-25

# CAMERA
cameraX=0

# SONIC FEEL (BALANCED FIX)
baseAccel=0.25
maxSpeed=16
friction=0.12

# --- ground detection ---
DIRT_COLOUR=(109,36,0)
TOLERANCE=15
HOVER_OFFSET=50
SCAN_DEPTH=300

loadSonicBg=image.load("pics/Sonic BG final.png")
sonicBg=transform.scale(loadSonicBg,(36720,4590))


#Functions

def colour_close(c1,c2,tol):
    return all(abs(c1[i]-c2[i])<=tol for i in range(3))


def find_ground_below(player):
    feet_y=int(player[Y]+player[rH])
    mid_x=width//2

    for scan_y in range(feet_y, min(feet_y+SCAN_DEPTH, height)):
        try:
            col=screen.get_at((mid_x,scan_y))[:3]
        except:
            break
        if colour_close(col,DIRT_COLOUR,TOLERANCE):
            return scan_y
    return None


def drawScene(player):
    global cameraX
    cameraX = player[X] - width//2

    screen.blit(sonicBg,(-cameraX,-2720))

    draw.rect(
        screen,
        blue,
        [width//2 - player[rW]//2, player[Y], player[rW], player[rH]]
    )


def move(p):
    keys = key.get_pressed()

    # jump
    if (keys[K_SPACE] or keys[K_UP]) and vel[Y] == 0:
        vel[Y] = jumpPower

    moving = False

    # acceleration 
    if keys[K_LEFT]:
        vel[X] -= baseAccel + max(0.05, abs(vel[X]) * 0.02)
        moving = True

    elif keys[K_RIGHT]:
        vel[X] += baseAccel + max(0.05, abs(vel[X]) * 0.02)
        moving = True

    # friction
    if not moving:
        if vel[X] > 0:
            vel[X] -= friction * (1 + abs(vel[X]) * 0.03)
            if vel[X] < 0:
                vel[X] = 0
        elif vel[X] < 0:
            vel[X] += friction * (1 + abs(vel[X]) * 0.03)
            if vel[X] > 0:
                vel[X] = 0


    if vel[X] > maxSpeed:
        vel[X] = maxSpeed
    if vel[X] < -maxSpeed:
        vel[X] = -maxSpeed


    if abs(vel[X]) < 0.15 and moving:
        vel[X] = 0.2 if vel[X] >= 0 else -0.2

    p[X] += vel[X]

    vel[Y] += gravity


def check(p):
    if vel[Y] < 0:
        p[Y] += vel[Y]
        return

    ground_y = find_ground_below(p)

    if ground_y is not None:
        target_feet = ground_y - HOVER_OFFSET
        feet = p[Y] + p[rH]

        if feet >= target_feet:
            p[Y] = target_feet - p[rH]
            vel[Y] = 0
        else:
            p[Y] += vel[Y]
    else:
        p[Y] += vel[Y]

    if p[Y] > height + 100:
        p[X] = 200
        p[Y] = 100
        vel[X] = 0
        vel[Y] = 0


def level1():
    running=True
    myClock=time.Clock()

    vel[X]=0
    vel[Y]=0

    player=Rect(200,100,80,80)

    while running:
        for evt in event.get():
            if evt.type==QUIT:
                running=False
            if evt.type==KEYDOWN and evt.key==K_ESCAPE:
                running=False

        drawScene(player)

        check(player)
        move(player)

        draw.rect(
            screen,
            blue,
            [width//2 - player[rW]//2, player[Y], player[rW], player[rH]]
        )

        myClock.tick(60)
        display.flip()


def mainMenu():
    running=True
    myClock=time.Clock()

    menuButtons=[Rect(100,100,200,50),
                 Rect(100,200,200,50)]

    while running:
        screen.fill(grey)
        mx,my=mouse.get_pos()

        for evt in event.get():
            if evt.type==QUIT:
                return "exit"
            if evt.type==MOUSEBUTTONDOWN:
                if menuButtons[1].collidepoint(mx,my):
                    return "level1"

        for b in menuButtons:
            draw.rect(screen,blue,b)

        gfont=font.SysFont(None,28)
        screen.blit(gfont.render("MENU",True,white),(160,110))
        screen.blit(gfont.render("LEVEL 1",True,white),(130,210))

        display.flip()
        myClock.tick(60)


# Game loop
page="mainMenu"
while page!="exit":
    if page=="mainMenu":
        page=mainMenu()
    elif page=="level1":
        page=level1()

quit()
