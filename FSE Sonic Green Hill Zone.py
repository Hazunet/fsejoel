#FSE By BW & JL
#Sonic The Hedgehog: Green Hill Zone

from pygame import *
from math import *


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

loadSonicBg=image.load("pics/Sonic BG final.png")
sonicBg=transform.scale(loadSonicBg,(36720,4590))





#Functions

def drawScene(player,platforms):
    vel[screenX] = width//2
    offset=vel[screenX]-player[X]
    screen.blit(sonicBg,(offset,-2720))

    for p in platforms:
        shifted=p.move(offset,0)
        draw.rect(screen,green,shifted)
    #!!!!!!!!!!!!!!!!!!!!!!
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

    #!!!!!!!!!!
    #vel[screenX]=p[X]  #camera always follows player exactly
    p[X]+=vel[X]#horizontal movement
    vel[Y]+=gravity#acceleration

def check(p,plats):
    #check if the players lands on one of the platforms
    for plat in plats:
        if p[X]+p[rW]>plat[X] and p[X]<plat[X]+plat[rW] and p[Y]+p[rH]<=plat[Y] and p[Y]+p[rH]+vel[Y]>=plat[Y]:
            vel[2]=plat[Y]
            vel[Y]=0#stop moving
            p[Y]=vel[2]-p[rH]
    p[Y]+=vel[Y]#vertical movement



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
    vel[2]=700
    vel[screenX]=200



    platforms=[Rect(100,700,1000,100),
               Rect(400,580,200,20),
               Rect(800,500,150,20),
               Rect(1200,450,200,20)]
    
    player=Rect(200,600,80,80)

    while running:


        for evt in event.get():
            if evt.type==QUIT:
                running=False
        
        check(player,platforms)
        move(player)
        drawScene(player,platforms)
        myClock.tick(60)

        counter+=1#frames



        display.flip()


    return "mainMenu"




def mainMenu():
    running = True
    myClock = time.Clock()
    #button rects
    menuButtons=[Rect(100,100,200,50),
                 Rect(100,200,200,50)#level 1
                 ]

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
                    #implement if collide with button
            


        for b in menuButtons:
            draw.rect(screen,blue,b)



        
        display.flip()
        myClock.tick(60)

    








#Page system


page="mainMenu"
while page !="exit":
    if page=="mainMenu":
        page=mainMenu()
    if page=="instructions":
        page=instructions()
    if page=="controls":
        page=controls()
    if page=="level1":
        page=level1()
            
quit()