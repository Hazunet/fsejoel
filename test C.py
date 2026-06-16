from pygame import *
from math import *


width,height=1200,900
screen=display.set_mode((width,height))

red=(255,0,0)
grey=(127,127,127)
black=(0,0,0)
blue=(0,0,255)
green=(0,255,0)
yellow=(255,255,0)
white=(255,255,255)
orange=(255,140,0)

gravity=1
X=0
Y=1
rW=2
grndLv=2

rH=3
screenX=3
vel=[0,0,700,200]
jumpPower=-25




loadSonicBg=image.load("pics/sonicbg.png")
sonicBg=transform.scale(loadSonicBg,(7200,900))
DETECTION_RADIUS=200

def drawScene(player,platforms,enemies):
    vel[screenX]=width//2
    offset=vel[screenX]-player[X]
    screen.blit(sonicBg,(offset,0))

    for p in platforms:
        shifted=p.move(offset,0)
        draw.rect(screen,green,shifted)
    for e in enemies:
        draw.rect(screen,red,[e[0]+offset,e[1],e[2],e[3]])
        ex_screen=int(e[0]+e[2]//2+offset)
        ey_screen=int(e[1]+e[3]//2)
        draw.circle(screen,yellow,(ex_screen,ey_screen),DETECTION_RADIUS,2)

    draw.rect(screen,blue,[vel[screenX]-player[rW]//2,player[Y],player[rW],player[rH]])


def move(p):
    keys=key.get_pressed()
    if keys[K_SPACE] and vel[Y]==0 and p[Y]+p[rH]==vel[grndLv]:
        vel[Y]=jumpPower

    vel[X]=0
    if keys[K_LEFT]:
        vel[X]=-5
    elif keys[K_RIGHT]:
        vel[X]=5
    p[X]+=vel[X]
    vel[Y]+=gravity

def check(p,plats):
    for plat in plats:
        if p[X]+p[rW]>plat[X] and p[X]<plat[X]+plat[rW] and p[Y]+p[rH]<=plat[Y] and p[Y]+p[rH]+vel[Y]>=plat[Y]:
            vel[2]=plat[Y]
            vel[Y]=0
            p[Y]=vel[2]-p[rH]
    p[Y]+=vel[Y]

def updateEnemies(enemies,player):

    for e in enemies:
        eW,eH=e[2],e[3]
        patrolLeft,patrolRight=e[4],e[5]
        dx=(player[X]+player[rW]//2)-(e[0]+eW//2)
        dy=(player[Y]+player[rH]//2)-(e[1]+eH//2)
        distance=sqrt(dx**2+dy**2)

        if distance<DETECTION_RADIUS:
            e[7]=True
        else:
            e[7]=False

        if e[7]:
            if dx>0:
                e[0]+=e[6]+1
            elif dx<0:
                e[0]-=e[6]+1
        else:
            if e[0]>=patrolRight:
                e[6]=-abs(e[6])
            elif e[0]<=patrolLeft:
                e[6]=abs(e[6])
            e[0]+=e[6]

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
    vel[2]=700
    vel[screenX]=200



    platforms=[Rect(100,700,1000,100),
               Rect(400,580,200,20),
               Rect(800,500,150,20),
               Rect(1200,450,200,20)]
    
    player=Rect(200,600,80,80)

    enemies=[[800,620,60,60,700,950,2,False]]

    while running:
        for evt in event.get():
            if evt.type==QUIT:
                running=False
        check(player,platforms)
        move(player)
        updateEnemies(enemies,player)
        drawScene(player,platforms,enemies)
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
        display.flip()
        myClock.tick(60)








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