#FSE By BW & JL
#Sonic The Hedgehog: Green Hill Zone

from pygame import *
from math import *

init()
width,height=1200,900
screen=display.set_mode((width,height))

#Colours
red=(255,0,0)
grey=(127,127,127)
black=(0,0,0)
blue=(0,0,255)
green=(0,255,0)
yellow=(255,255,0)
white=(255,255,255)

#Misc
gravity=1
X=0
Y=1
rW=2
grndLv=2
rH=3
screenX=3

vel=[0,0,700,200]
jumpPower=-25

# --- colour detection settings ---
DIRT_COLOUR=(69,23,0)
WALL_COLOUR=(59,20,0)
TOLERANCE=15
HOVER_OFFSET=50
SCAN_DEPTH=300
WALL_SCAN_DIST=60

loadSonicBg=image.load("pics/Sonic BG final.png")
sonicBg=transform.scale(loadSonicBg,(36720,4590))


#Functions

def colour_close(c1,c2,tol):
    return all(abs(c1[i]-c2[i])<=tol for i in range(3))

def find_ground_below(player):
    """Scan downward from player feet, return screen Y of first dirt pixel or None."""
    feet_y=int(player[Y]+player[rH])
    mid_x=int(vel[screenX])
    mid_x=max(0,min(width-1,mid_x))
    for scan_y in range(feet_y, min(feet_y+SCAN_DEPTH, height)):
        try:
            col=screen.get_at((mid_x,scan_y))[:3]
        except:
            break
        if colour_close(col,DIRT_COLOUR,TOLERANCE):
            return scan_y
    return None

def check_wall(player):
    """Scan left and right from player sides, return 'left', 'right', or None."""
    scan_y=int(player[Y]+player[rH]//2)
    scan_y=max(0,min(height-1,scan_y))
    screen_x=int(vel[screenX])

    right_edge=screen_x+player[rW]//2
    for scan_x in range(right_edge, min(right_edge+WALL_SCAN_DIST, width)):
        try:
            col=screen.get_at((scan_x,scan_y))[:3]
        except:
            break
        if colour_close(col,WALL_COLOUR,0):
            return 'right'

    left_edge=screen_x-player[rW]//2
    for scan_x in range(left_edge, max(left_edge-WALL_SCAN_DIST, 0), -1):
        try:
            col=screen.get_at((scan_x,scan_y))[:3]
        except:
            break
        if colour_close(col,WALL_COLOUR,0):
            return 'left'

    return None

def drawScene(player,offset):
    screen.blit(sonicBg,(offset,-2720))
    draw.rect(screen,blue,[vel[screenX]-player[rW]//2,player[Y],player[rW],player[rH]])

def move(p, wall):
    keys=key.get_pressed()

    if (keys[K_SPACE] or keys[K_UP]) and vel[Y]==0:
        vel[Y]=jumpPower

    vel[X]=0
    if keys[K_LEFT]:  vel[X]=-30
    if keys[K_RIGHT]: vel[X]=30

    if wall=='right' and vel[X]>0:
        vel[X]=0
    if wall=='left'  and vel[X]<0:
        vel[X]=0

    p[X]+=vel[X]
    vel[Y]+=gravity

def check(p):
    """Colour-based ground detection."""
    if vel[Y]<0:
        p[Y]+=vel[Y]
        return

    ground_y=find_ground_below(p)

    if ground_y is not None:
        target_feet=ground_y-HOVER_OFFSET
        feet=p[Y]+p[rH]
        if feet>=target_feet:
            p[Y]=target_feet-p[rH]
            vel[Y]=0
        else:
            p[Y]+=vel[Y]
    else:
        p[Y]+=vel[Y]

    if p[Y]>height+100:
        p[X]=200
        p[Y]=100
        vel[X]=0
        vel[Y]=0


#Screens

def instructions():
    draw.rect(screen,yellow,(0,0,width,height))

def controls():
    draw.rect(screen,red,(0,0,width,height))

def level1():
    running=True
    myClock=time.Clock()
    counter=0

    vel[X]=0
    vel[Y]=0
    vel[grndLv]=700
    vel[screenX]=width//2

    player=Rect(200,100,80,80)

    while running:
        for evt in event.get():
            if evt.type==QUIT:
                running=False
            if evt.type==KEYDOWN and evt.key==K_ESCAPE:
                running=False

        offset=width//2-player[X]
        drawScene(player,offset)

        check(player)
        wall=check_wall(player)
        move(player,wall)

        draw.rect(screen,blue,[vel[screenX]-player[rW]//2,player[Y],player[rW],player[rH]])

        gfont=font.SysFont(None,24)
        feet_y=int(player[Y]+player[rH])
        mid_x=int(vel[screenX])
        try:
            col=screen.get_at((mid_x,feet_y))[:3]
        except:
            col=(0,0,0)
        screen.blit(gfont.render(f"feet pixel colour: {col}",True,black),(10,10))
        screen.blit(gfont.render(f"wall: {wall}",True,black),(10,34))
        screen.blit(gfont.render(f"player world X: {int(player[X])}  Y: {int(player[Y])}",True,black),(10,58))
        screen.blit(gfont.render("arrows/WASD move   Space jump   Esc back",True,black),(10,82))

        myClock.tick(60)
        counter+=1
        display.flip()

    return "mainMenu"


def mainMenu():
    running=True
    myClock=time.Clock()
    menuButtons=[Rect(100,100,200,50),
                 Rect(100,200,200,50)]

    while running:
        screen.fill(grey)
        mx,my=mouse.get_pos()
        mb=mouse.get_pressed()

        for evt in event.get():
            if evt.type==QUIT:
                return "exit"
            if evt.type==MOUSEBUTTONDOWN:
                if evt.button==1:
                    if menuButtons[1].collidepoint(mx,my):
                        return "level1"

        for b in menuButtons:
            draw.rect(screen,blue,b)

        gfont=font.SysFont(None,28)
        screen.blit(gfont.render("MENU",True,white),(160,110))
        screen.blit(gfont.render("LEVEL 1",True,white),(130,210))

        display.flip()
        myClock.tick(60)


#Page system
page="mainMenu"
while page!="exit":
    if page=="mainMenu":
        page=mainMenu()
    if page=="instructions":
        page=instructions()
    if page=="controls":
        page=controls()
    if page=="level1":
        page=level1()

quit()