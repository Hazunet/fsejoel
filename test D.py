from pygame import *


def drawScene(screen,bgPic,p,plats,red,white,X,Y):

    offset=200-p[X]
    screen.blit(bgPic,(offset,0))
    draw.rect(screen,red,[200,p[Y],p.width,p.height])

    for plat in plats:
        plat=plat.move(offset,0)
        draw.rect(screen,white,plat)




def move(p,v,on_ground,accel,decNum,friction,max_speed,gravity,jump_power,X,Y):
    keys=key.get_pressed()


    if keys[K_LEFT]:
        if v[X]>0:
            v[X]-=decNum
        elif v[X]>-max_speed:
            v[X]-=accel

    elif keys[K_RIGHT]:
        if v[X]<0:
            v[X]+=decNum

        elif v[X]<max_speed:
            v[X]+=accel

    else:
        v[X]*=friction
        if abs(v[X])<0.2:
            v[X]=0

    if keys[K_SPACE] and on_ground:
        v[Y]=jump_power
        on_ground=False


    v[Y]+=gravity
    p[X]+=v[X]

    if not on_ground:
        p[Y]+=v[Y]

    if p[Y]>=190:
        p[Y]=190
        v[Y]=0
        on_ground=True
    if p[X]<200:
        p[X]=200
        v[X]=0
    elif p[X]>2240:
        p[X]=2240
        v[X]=0

    return on_ground





width,height=400,210
screen=display.set_mode((width,height))




red=(255,0,0)
white=(255,255,255)

bgPic=image.load("pics/sonicbg.png")
X=0
Y=1
v=[0.0,0.0,210]

accel=0.15
decNum=1.0
friction=0.985
max_speed=14.0
gravity=0.5
jump_power=-10.0
on_ground=True


player=Rect(200,190,20,20)

platforms=[Rect(270,170,60,20),Rect(380,150,60,20),Rect(780,150,60,20)]

myClock=time.Clock()
running=True

while running:

    for evt in event.get():
        if evt.type==QUIT:
            running=False


    on_ground=move(player,v,on_ground,accel,decNum,friction,max_speed,gravity,jump_power,X,Y)
    drawScene(screen,bgPic,player,platforms,red,white,X,Y)


    myClock.tick(60)
    display.flip()

quit()