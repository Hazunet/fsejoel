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
TOLERANCE=15        # wiggle room for colour matching
HOVER_OFFSET=50      # pixels above the dirt surface the player stands
SCAN_DEPTH=300      # how far below feet we scan

loadSonicBg=image.load("pics/Sonic BG final.png")
sonicBg=transform.scale(loadSonicBg,(36720,4590))


#Functions

def colour_close(c1,c2,tol):
    return all(abs(c1[i]-c2[i])<=tol for i in range(3))

def find_ground_below(player):
    """Scan downward from player feet, return screen Y of first dirt pixel or None."""
    feet_y=int(player[Y]+player[rH])
    mid_x=int(vel[screenX])   # player is always drawn at screen center
    mid_x=max(0,min(width-1,mid_x))

    for scan_y in range(feet_y, min(feet_y+SCAN_DEPTH, height)):
        try:
            col=screen.get_at((mid_x,scan_y))[:3]
        except:
            break
        if colour_close(col,DIRT_COLOUR,TOLERANCE):
            return scan_y
    return None

def drawScene(player,offset):
    screen.blit(sonicBg,(offset,-2720))
    draw.rect(screen,blue,[vel[screenX]-player[rW]//2,player[Y],player[rW],player[rH]])

def move(p):
    keys=key.get_pressed()

    if (keys[K_SPACE] or keys[K_UP]) and vel[Y]==0:
        vel[Y]=jumpPower

    vel[X]=0
    if keys[K_LEFT]:  vel[X]=-30
    if keys[K_RIGHT]: vel[X]=30

    p[X]+=vel[X]
    vel[Y]+=gravity

def check(p):
    """Colour-based ground detection."""
    if vel[Y]<0:
        # jumping upward — just move, no ground snap
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

    # respawn if fallen off screen
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

        # background MUST be drawn first so screen.get_at reads correct pixels
        offset=width//2-player[X]
        drawScene(player,offset)

        # then check collision (reads pixels already on screen)
        check(player)
        move(player)

        # redraw player on top after position is updated
        draw.rect(screen,blue,[vel[screenX]-player[rW]//2,player[Y],player[rW],player[rH]])

        # debug info
        gfont=font.SysFont(None,24)
        feet_y=int(player[Y]+player[rH])
        mid_x=int(vel[screenX])
        try:
            col=screen.get_at((mid_x,feet_y))[:3]
        except:
            col=(0,0,0)
        screen.blit(gfont.render(f"feet pixel colour: {col}",True,black),(10,10))
        screen.blit(gfont.render(f"player world X: {int(player[X])}  Y: {int(player[Y])}",True,black),(10,34))
        screen.blit(gfont.render("arrows/WASD move   Space jump   Esc back",True,black),(10,58))

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