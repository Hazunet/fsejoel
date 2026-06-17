#version n+

from pygame import *
from math import *
import random

init()
mixer.init() # Ensure mixer is running
w, h = 1200, 900
screen = display.set_mode((w, h))

# --- Loading Screen ---
# Play SEGA sound effect immediately 
mixer.music.load("sega.mp3")
mixer.music.play()

rawSegaImg = image.load("pics/segaLoading.png") 
imgW, imgH = rawSegaImg.get_size()
scale = min(w / imgW, h / imgH) 
scaledW = int(imgW * scale) 
scaledH = int(imgH * scale) 
segaImg = transform.scale(rawSegaImg, (scaledW, scaledH))
segaX = (w - scaledW) // 2 
segaY = (h - scaledH) // 2 

loadingStart = time.get_ticks() 
while time.get_ticks() - loadingStart < 2000: 
    for e in event.get(): 
        if e.type == QUIT: 
            quit() 
    screen.fill((255, 255, 255)) 
    screen.blit(segaImg, (segaX, segaY)) 
    display.flip() 

# Stop SEGA audio before moving forward
mixer.music.stop()

grey = (127, 127, 127)
blue = (0, 0, 255)
white = (255, 255, 255)
dirt = (109, 36, 0)
red = (255, 0, 0)
orange = (255, 127, 0)
yellow = (255, 255, 0)
lightBlue = (0, 191, 255)

X = 0
Y = 1
W = 2
H = 3
ROW = 4
COL = 5


bgImg     = transform.scale(image.load("pics/alternateBG.png"), (36720, 4590))
menuBgImg = transform.scale(image.load("pics/sonicMenuBG.png"), (w, h))

def addPics(folder, name, start, end):
    pics = []
    for i in range(start, end):
        pics.append(image.load(f"pics/{folder}/{name}{i}.png"))
    return pics

sonicRight = addPics("sonic sprites", "sonic", 1, 10)
sonicLeft  = [transform.flip(img, True, False) for img in sonicRight]
sonicIdle  = [sonicRight[0]]
sonicJump  = [image.load("pics/sonic sprites/sonicjump.png")]

sonicPics = [sonicRight, sonicLeft, sonicIdle, sonicJump]

coinPics = addPics("coins", "coin", 1, 4)


# Roll & Slide Animations
sonicRollStart = addPics("sonic sprites", "sonicroll", 1, 6)
sonicBallLoop  = [image.load("pics/sonic sprites/mainsonicroll.png")]
sonicSlide     = addPics("sonic sprites", "sonicslide", 1, 3)

sonicPics.append(sonicSlide)  # index 4 = slide

fishPics = addPics("fish", "fish", 1, 3)
crabPics = addPics("crab", "crab", 1, 5)
jumpPics = addPics("jump", "jump", 1, 3)

monitorActiveImg = image.load("pics/powerup/powerup1.png")
monitorBrokenImg = image.load("pics/powerup/powerup2.png")
abilityItemImg   = image.load("pics/powerup/ability.png")

buzzFlightPics = addPics("buzzbomber", "buzz", 1, 6)
buzzShotPic    = image.load("pics/buzzbomber/buzzshot.png")

def updateCoins(coins):
    for coin in coins:
        coin[4] += 0.15
        if coin[4] >= len(coinPics):
            coin[4] = 0

def drawHud(cam, coinCount, lives, coins, elapsedTime, powerTimer, score):
    for coin in coins:
        if coin[5] == False:
            frame = transform.scale(coinPics[int(coin[4])], (coin[2], coin[3]))
            screen.blit(frame, (coin[0] - cam[0], coin[1] - cam[1]))

    f = font.SysFont(None, 36)
    coinIcon = transform.scale(coinPics[0], (28, 28))
    screen.blit(coinIcon, (10, 10))
    screen.blit(f.render(f"x {coinCount}", True, white), (44, 14))
    screen.blit(f.render(f"LIVES: {lives}", True, white), (10, 50))

    seconds = int(elapsedTime % 60)
    minutes = int(elapsedTime // 60)
    secStr = f"0{seconds}" if seconds < 10 else f"{seconds}"
    screen.blit(f.render(f"TIME: {minutes}:{secStr}", True, white), (10, 90))

    screen.blit(f.render(f"SCORE: {score}", True, white), (10, 170))
    if powerTimer > 0:
        pSecs = int((powerTimer / 60) + 1)
        screen.blit(f.render(f"INVINCIBLE: {pSecs}s", True, yellow), (10, 130))

def checkCoinCollect(p, coinCount, coins):
    playerRect = Rect(p[X], p[Y], p[W], p[H])
    for coin in coins:
        if coin[5] == False:
            if playerRect.colliderect(Rect(coin[0], coin[1], coin[2], coin[3])):
                coin[5] = True
                coinCount += 1
    return coinCount

def updateDroppedCoins(cam, droppedCoins):
    for dc in droppedCoins:
        dc[6] += 0.15
        if dc[6] >= len(coinPics):
            dc[6] = 0

        dc[0] += dc[4]
        dc[1] += dc[5]
        dc[5] += 0.5

        dummyP = [dc[0], dc[1], dc[2], dc[3]]
        gY = getGround(dummyP, cam)

        if gY != None:
            if dc[1] + dc[3] >= gY - 50:
                dc[1] = gY - 50 - dc[3]
                dc[5] = -dc[5] * 0.75
                dc[4] *= 0.9

        dc[7] -= 1

    return [dc for dc in droppedCoins if dc[7] > 0]

def drawDroppedCoins(cam, droppedCoins):
    for dc in droppedCoins:
        frame = transform.scale(coinPics[int(dc[6])], (dc[2], dc[3]))
        screen.blit(frame, (dc[0] - cam[0], dc[1] - cam[1]))

def collectDroppedCoins(p, coinCount, droppedCoins):
    playerRect = Rect(p[X], p[Y], p[W], p[H])
    newCoinCount = coinCount
    for dc in droppedCoins:
        if dc[7] < 160:
            if playerRect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
                newCoinCount += 1

    updatedList = []
    for dc in droppedCoins:
        if dc[7] < 160:
            if playerRect.colliderect(Rect(dc[0], dc[1], dc[2], dc[3])):
                pass
            else:
                updatedList.append(dc)
        else:
            updatedList.append(dc)

    return newCoinCount, updatedList

def updateEnemies(cam, enemies, p):
    for enemy in enemies:
        enemy[7] += 0.15
        if enemy[7] >= len(crabPics):
            enemy[7] = 0.0

        dist = sqrt((enemy[0] - p[X])**2 + (enemy[1] - p[Y])**2)

        if dist < 350:
            if enemy[0] < p[X]:
                enemy[6] = abs(enemy[6])
                enemy[0] += 2.5
            else:
                enemy[6] = -abs(enemy[6])
                enemy[0] -= 2.5
        else:
            enemy[0] += enemy[6]
            if enemy[0] <= enemy[4]:
                enemy[0] = enemy[4]
                enemy[6] = abs(enemy[6])
            elif enemy[0] >= enemy[5]:
                enemy[0] = enemy[5]
                enemy[6] = -abs(enemy[6])

        dummyEnemy = [enemy[0], enemy[1], enemy[2], enemy[3]]
        gY = getGround(dummyEnemy, cam)
        if gY != None:
            enemy[1] = gY - enemy[3]

        if dist < 350:
            if enemy[4] <= p[X]:
                if p[X] <= enemy[5]:
                    if enemy[0] < p[X]:
                        enemy[6] = abs(enemy[6])
                    else:
                        enemy[6] = -abs(enemy[6])
                    enemy[0] += enemy[6] * 2.5
                else:
                    enemy[0] += enemy[6]
                    if enemy[0] <= enemy[4]:
                        enemy[0] = enemy[4]
                        enemy[6] = abs(enemy[6])
                    elif enemy[0] >= enemy[5]:
                        enemy[0] = enemy[5]
                        enemy[6] = -abs(enemy[6])
            else:
                enemy[0] += enemy[6]
                if enemy[0] <= enemy[4]:
                    enemy[0] = enemy[4]
                    enemy[6] = abs(enemy[6])
                elif enemy[0] >= enemy[5]:
                    enemy[0] = enemy[5]
                    enemy[6] = -abs(enemy[6])
        else:
            enemy[0] += enemy[6]
            if enemy[0] <= enemy[4]:
                enemy[0] = enemy[4]
                enemy[6] = abs(enemy[6])
            elif enemy[0] >= enemy[5]:
                enemy[0] = enemy[5]
                enemy[6] = -abs(enemy[6])

        dummyEnemy = [enemy[0], enemy[1], enemy[2], enemy[3]]
        gY = getGround(dummyEnemy, cam)
        if gY != None:
            enemy[1] = gY - enemy[3]

def updateFishEnemies(fishes):
    for fish in fishes:
        fish[8] += 0.15
        if fish[8] >= len(fishPics):
            fish[8] = 0

        if fish[4] == False:
            fish[7] -= 1
            if fish[7] <= 0:
                fish[4] = True
                fish[5] = -14
        else:
            fish[1] += fish[5]
            fish[5] += 0.3

            if fish[1] >= fish[6]:
                fish[1] = fish[6]
                fish[4] = False
                fish[5] = 0
                fish[7] = 60

def updateBuzzBombers(bombers, p, projectiles):
    for b in bombers:
        b[9] += 0.20
        if b[9] >= len(buzzFlightPics):
            b[9] = 0.0

        if b[8] == True:
            if b[7] > 0:
                b[7] -= 1
                if b[7] == 0:
                    if p[X] < b[0]:
                        projVx = -5
                        b[6] = -abs(b[6])
                    else:
                        projVx = 5
                        b[6] = abs(b[6])
                    projectiles.append([b[0] + 20, b[1] + 40, 20, 10, projVx, 5])
            else:
                b[8] = False
                b[7] = 120
        else:
            if b[7] > 0:
                b[7] -= 1

            b[0] += b[6]
            if b[0] <= b[4]:
                b[0] = b[4]
                b[6] = abs(b[6])
            elif b[0] >= b[5]:
                b[0] = b[5]
                b[6] = -abs(b[6])

            if b[7] <= 0 and abs(p[X] - b[0]) < 300 and p[Y] > b[1]:
                b[8] = True
                b[7] = 60

def updateProjectiles(projectiles):
    updated = []
    for pr in projectiles:
        pr[0] += pr[4]
        pr[1] += pr[5]
        if -500 < pr[0]:
            if pr[0] < 40000:
                if pr[1] < h + 500:
                    updated.append(pr)
    return updated

def drawEnemies(cam, enemies, fishes, bombers, projectiles, winBox, jumpPads, monitor, star):
    draw.rect(screen, yellow, (winBox[0] - cam[0], winBox[1] - cam[1], winBox[2], winBox[3]))

    for jumpPad in jumpPads:
        if jumpPad[4] == True:
            frame = jumpPics[1]
        else:
            frame = jumpPics[0]
        frameScaled = transform.scale(frame, (jumpPad[2], jumpPad[3]))
        screen.blit(frameScaled, (jumpPad[0] - cam[0], jumpPad[1] - cam[1]))

    if monitor[4] == False:
        mFrame = transform.scale(monitorActiveImg, (monitor[2], monitor[3]))
        screen.blit(mFrame, (monitor[0] - cam[0], monitor[1] - cam[1]))
    else:
        brokenW = monitor[2]
        brokenH = monitor[3] // 2
        mFrame = transform.scale(monitorBrokenImg, (brokenW, brokenH))
        screen.blit(mFrame, (monitor[0] - cam[0], monitor[1] + brokenH - cam[1]))

    if star[2] == True:
        abilityScaled = transform.scale(abilityItemImg, (60, 60))
        screen.blit(abilityScaled, (int(star[0] - cam[0] - 30), int(star[1] - cam[1] - 30)))

    for enemy in enemies:
        frame = crabPics[int(enemy[7])]
        frameScaled = transform.scale(frame, (enemy[2], enemy[3]))
        if enemy[6] < 0:
            frameScaled = transform.flip(frameScaled, True, False)
        screen.blit(frameScaled, (enemy[0] - cam[0], enemy[1] - cam[1]))

    for fish in fishes:
        frame = fishPics[int(fish[8])]
        frameScaled = transform.scale(frame, (fish[2], fish[3]))
        if fish[5] > 0:
            frameScaled = transform.flip(frameScaled, False, True)
        screen.blit(frameScaled, (fish[0] - cam[0], fish[1] - cam[1]))

    for b in bombers:
        if b[8] == True:
            bFrame = buzzShotPic
        else:
            bFrame = buzzFlightPics[int(b[9])]
        bScaled = transform.scale(bFrame, (b[2], b[3]))
        if b[6] > 0:
            bScaled = transform.flip(bScaled, True, False)
        screen.blit(bScaled, (b[0] - cam[0], b[1] - cam[1]))

    for pr in projectiles:
        draw.rect(screen, yellow, (pr[0] - cam[0], pr[1] - cam[1], pr[2], pr[3]))

def checkEnemyCollision(p, vel, invincibility, coinCount, lives, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, godMode):
    playerRect = Rect(p[X], p[Y], p[W], p[H])

    destroyedEnemies    = []
    destroyedFishes     = []
    destroyedBombers    = []
    destroyedProjectiles = []

    hitByHarmful = False
    enemyX = 0

    for enemy in enemies:
        enemyRect = Rect(enemy[0], enemy[1], enemy[2], enemy[3])
        if playerRect.colliderect(enemyRect):
            if isRolling == True or godMode:
                destroyedEnemies.append(enemy)
                vel[1] = -10
            elif vel[1] > 0:
                destroyedEnemies.append(enemy)
                vel[1] = -10
            else:
                hitByHarmful = True
                enemyX = enemy[0]

    for fish in fishes:
        fishRect = Rect(fish[0], fish[1], fish[2], fish[3])
        if playerRect.colliderect(fishRect):
            if isRolling == True or godMode:
                destroyedFishes.append(fish)
                vel[1] = -10
            elif vel[1] > 0:
                destroyedFishes.append(fish)
                vel[1] = -10
            else:
                hitByHarmful = True
                enemyX = fish[0]

    for b in bombers:
        bomberRect = Rect(b[0], b[1], b[2], b[3])
        if playerRect.colliderect(bomberRect):
            if isRolling == True or godMode:
                destroyedBombers.append(b)
                vel[1] = -10
            elif vel[1] > 0:
                destroyedBombers.append(b)
                vel[1] = -10
            else:
                hitByHarmful = True
                enemyX = b[0]

    for pr in projectiles:
        projRect = Rect(pr[0], pr[1], pr[2], pr[3])
        if playerRect.colliderect(projRect):
            if isRolling == True or godMode:
                destroyedProjectiles.append(pr)
            else:
                hitByHarmful = True
                enemyX = pr[0]

    enemies[:]     = [e  for e  in enemies     if e  not in destroyedEnemies]
    fishes[:]      = [f  for f  in fishes      if f  not in destroyedFishes]
    bombers[:]     = [b  for b  in bombers     if b  not in destroyedBombers]
    projectiles[:] = [pr for pr in projectiles if pr not in destroyedProjectiles]

    if hitByHarmful == True and not godMode:
        if invincibility <= 0:
            vel[1] = -12
            if p[X] < enemyX:
                vel[0] = -10
            else:
                vel[0] = 10

            invincibility = 120

            if coinCount > 0:
                coinsToDrop = min(coinCount, 20)
                for i in range(coinsToDrop):
                    angle = random.uniform(0, 2 * pi)
                    speed = random.uniform(4, 9)
                    vx = cos(angle) * speed
                    vy = sin(angle) * speed - 3
                    droppedCoins.append([p[X], p[Y], 32, 32, vx, vy, 0.0, 180])
                coinCount = 0
            else:
                lives -= 1
                
                p[X], p[Y] = 200, 100
                vel[0], vel[1] = 0, 0
                invincibility = 0

    return invincibility, coinCount, lives

def getGround(p, cam):
    sx = int(p[X] - cam[0] + (p[W] / 2))
    sy = int(p[Y] - cam[1] + p[H])

    if sx < 0 or sx >= w:
        return None

    for y in range(sy, sy + 300):
        if 0 <= y < h:
            c = screen.get_at((sx, y))[:3]
            if c[0] == 69 and c[1] == 23 and c[2] == 0:  # exact match only
                return y + cam[1]
        else:
            break
    return None

def getWall(p, cam):
    leftX  = int(p[X] - cam[0])
    rightX = int(p[X] - cam[0] + p[W])

    wallLeft  = False
    wallRight = False

    # Sample multiple heights along the player's side
    for frac in [0.2, 0.4, 0.6, 0.8]:
        sampleY = int(p[Y] - cam[1] + p[H] * frac)
        if not (0 <= sampleY < h):
            continue

        if 0 <= leftX < w:
            c = screen.get_at((leftX, sampleY))[:3]
            if c[0] == 59 and c[1] == 20 and c[2] == 0:
                wallLeft = True

        if 0 <= rightX < w:
            c = screen.get_at((rightX, sampleY))[:3]
            if c[0] == 59 and c[1] == 20 and c[2] == 0:
                wallRight = True

    return wallLeft, wallRight

def updatePhysics(p, vel, cam, isJumping, invincibility, isRolling):
    fallDeath = False

    # Sub-stepping loop: only activates when falling downward quickly (vel[1] > 0)
    # Otherwise, it falls back to your exact single-step physics
    if vel[1] > 5:
        steps = int(vel[1])
        for _ in range(steps):
            p[Y] += 1
            groundY = getGround(p, cam)
            if groundY != None:
                if p[Y] + p[H] >= groundY - 50:
                    p[Y] = groundY - 50 - p[H]
                    vel[1] = 0
                    isJumping = False
                    break # Stop sub-stepping immediately, we hit the line!
    else:
        # Your exact original vertical movement line
        p[Y] += vel[1]
        groundY = getGround(p, cam)
        if groundY != None:
            if p[Y] + p[H] >= groundY - 50:
                p[Y] = groundY - 50 - p[H]
                vel[1] = 0
                isJumping = False

    # Your exact original wall collision code
    wallLeft, wallRight = getWall(p, cam)
    if wallLeft and vel[0] < 0:
        vel[0] = 0
        p[X] = int(cam[0] + (int(p[X] - cam[0]) + 1))  # snap to just right of wall
    if wallRight and vel[0] > 0:
        vel[0] = 0
        p[X] = int(cam[0] + (int(p[X] + p[W] - cam[0]) - p[W] - 1))  # snap to just left of wall

    # Your exact original boundary/death code
    if p[Y] > h + 200:
        p[X] = 200
        p[Y] = 100
        vel[0] = 0
        vel[1] = 0
        isJumping = False
        isRolling = False
        fallDeath = True

    if invincibility > 0:
        invincibility -= 1

    return isJumping, invincibility, fallDeath, isRolling

def handleInput(p, vel, isJumping, invincibility, isRolling, xPressedLast, rollFrame):
    keys = key.get_pressed()

    if invincibility < 100 or True:
        if keys[K_SPACE] or keys[K_UP]:
            if isJumping == False:
                vel[1] = -25
                isJumping = True
                isRolling = False

        if keys[K_x]:
            if xPressedLast == False:
                xPressedLast = True
                if isRolling == True:
                    isRolling = False
                elif isJumping == False:
                    isRolling = True
                    rollFrame = 0.0
        else:
            xPressedLast = False

        if keys[K_LEFT]:
            if isRolling == True:
                vel[0] -= 0.35
            else:
                vel[0] -= 0.25 + max(0.05, abs(vel[0]) * 0.02)
        elif keys[K_RIGHT]:
            if isRolling == True:
                vel[0] += 0.35
            else:
                vel[0] += 0.25 + max(0.05, abs(vel[0]) * 0.02)

    if isRolling:
        speed = abs(vel[0])
        rollFrame += 0.2 + speed * 0.02
    elif isJumping:
        p[ROW] = 3
        p[COL] = 0
    else:
        moving = keys[K_LEFT] or keys[K_RIGHT]

        if not moving and abs(vel[0]) > 6.0:
            p[ROW] = 4
            p[COL] += 0.15
            if p[COL] >= len(sonicPics[4]):
                p[COL] = 0
        else:
            if keys[K_LEFT]:
                p[ROW] = 1
            elif keys[K_RIGHT]:
                p[ROW] = 0

            if not moving:
                p[ROW] = 2
                p[COL] = 0
            else:
                speed = abs(vel[0])
                p[COL] += 0.1 + speed * 0.03
                numFrames = len(sonicPics[p[ROW]])
                if p[COL] >= numFrames:
                    p[COL] = 0

    if keys[K_LEFT] == False and keys[K_RIGHT] == False:
        fric = 0.025 if isRolling else 0.12
        if vel[0] > 0:
            vel[0] -= fric * (1 + abs(vel[0]) * 0.03)
            if vel[0] < 0: vel[0] = 0
        elif vel[0] < 0:
            vel[0] += fric * (1 + abs(vel[0]) * 0.03)
            if vel[0] > 0: vel[0] = 0

    maxSpeed = 22 if isRolling else 16
    vel[0] = max(-maxSpeed, min(maxSpeed, vel[0]))
    p[X] += vel[0]
    vel[1] += 1

    MAP_LEFT  = 0
    MAP_RIGHT = 36720
    p[X] = max(MAP_LEFT, min(p[X], MAP_RIGHT - p[W]))

    return isJumping, isRolling, xPressedLast, rollFrame

def render(p, cam, coinCount, lives, invincibility, coins, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, elapsedTime, winBox, jumpPads, monitor, star, powerTimer, rollFrame, vel, score):
    cam[0] += ((p[X] - w // 2) - cam[0]) * 0.08
    cam[1] += ((p[Y] - h // 2) - cam[1]) * 0.08

    # Clamp camera so it never shows outside the background
    BG_W, BG_H = 36720, 4590
    cam[0] = max(0, min(cam[0], BG_W - w))
    cam[1] = max(-2720, min(cam[1], BG_H - 2720 - h))

    screen.blit(bgImg, (-cam[0], -2720 - cam[1]))

    drawHud(cam, coinCount, lives, coins, elapsedTime, powerTimer, score)
    drawDroppedCoins(cam, droppedCoins)
    drawEnemies(cam, enemies, fishes, bombers, projectiles, winBox, jumpPads, monitor, star)

    godMode = powerTimer > 0

    shouldDraw = True
    if not godMode:
        if invincibility > 0:
            if invincibility % 4 >= 2:
                shouldDraw = False

    if shouldDraw:
        if isRolling == True:
            if rollFrame < 5:
                frame = sonicRollStart[int(rollFrame)]
            else:
                frame = sonicBallLoop[0]

            if vel[0] < 0:
                frame = transform.flip(frame, True, False)

            origW = frame.get_width()
            origH = frame.get_height()
            frameScaled = transform.scale(frame, (origW * 3, origH * 3))

            if godMode and (powerTimer % 4 < 2):
                tintSurf = Surface((origW * 3, origH * 3), SRCALPHA)
                tintSurf.fill((255, 255, 0, 140))
                frameScaled = frameScaled.copy()
                frameScaled.blit(tintSurf, (0, 0), special_flags=BLEND_RGBA_MULT)

            drawX = p[X] - cam[0] - (origW * 3 - p[W]) // 2
            drawY = p[Y] - cam[1] - (origH * 3 - p[H]) // 2
            screen.blit(frameScaled, (drawX, drawY))
        else:
            frame = sonicPics[p[ROW]][int(p[COL])]
            origW = frame.get_width()
            origH = frame.get_height()
            frameScaled = transform.scale(frame, (origW * 3, origH * 3))

            if (p[ROW] == 4 or p[ROW] == 3) and vel[0] < 0:
                frameScaled = transform.flip(frameScaled, True, False)

            if godMode and (powerTimer % 4 < 2):
                tintSurf = Surface((origW * 3, origH * 3), SRCALPHA)
                tintSurf.fill((255, 255, 0, 140))
                frameScaled = frameScaled.copy()
                frameScaled.blit(tintSurf, (0, 0), special_flags=BLEND_RGBA_MULT)

            drawX = p[X] - cam[0] - (origW * 3 - p[W]) // 2
            drawY = p[Y] - cam[1] - (origH * 3 - p[H]) // 2
            screen.blit(frameScaled, (drawX, drawY))

            if godMode:
                draw.circle(screen, white, (int(p[X] - cam[0] + random.randint(0, p[W])), int(p[Y] - cam[1] - 10)), 5)

def drawVictoryScreen(elapsedTime, score):
    # --- PLAY WIN MUSIC ---
    mixer.music.load("win.mp3")
    mixer.music.play()

    # --- USE PIXEL FONT ---
    fLarge = font.Font("font.otf", 72)
    fSmall = font.Font("font.otf", 48)

    seconds = int(elapsedTime % 60)
    minutes = int(elapsedTime // 60)
    secStr  = f"0{seconds}" if seconds < 10 else f"{seconds}"

    finalScore = score

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        overlay = Surface((w, h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(10)
        screen.blit(overlay, (0, 0))

        txtWin      = fLarge.render("YOU WON!", True, yellow)
        txtTime     = fSmall.render(f"Final Time: {minutes}:{secStr}", True, white)
        txtScore    = fSmall.render(f"Final Score: {finalScore}", True, yellow)
        txtExit     = fSmall.render("Press ESC to return to Menu", True, grey)

        screen.blit(txtWin,   (w // 2 - txtWin.get_width()   // 2, h // 2 - 100))
        screen.blit(txtTime,  (w // 2 - txtTime.get_width()  // 2, h // 2 - 20))
        screen.blit(txtScore, (w // 2 - txtScore.get_width() // 2, h // 2 + 50))
        screen.blit(txtExit,  (w // 2 - txtExit.get_width()  // 2, h // 2 + 130))

        display.flip()

def storyScreen():
    c = time.Clock()
    
    titleFont = font.Font("font.otf", 36)
    bodyFont  = font.Font("font.otf", 18)
    promptFont = font.Font("font.otf", 14)
    
    pages = [
        [
            "THE LEGEND BEGINS...",
            "",
            "Long ago on Planet Mobius, Sonic was a regular, ordinary brown hedgehog.",
            "He loved freedom and running across the green hills, but he wasn't yet",
            "the supersonic hero the world knows today."
        ],
        [
            "DR. OVI KINTOBOR",
            "",
            "Sonic befriended a brilliant, kind-hearted scientist named Dr. Ovi Kintobor.",
            "Kintobor wanted to rid the entire planet of evil forces using a powerful",
            "machine called the Retro-Orbital Chaos Compressor (R.O.C.C.),",
            "which was powered by the mysterious Chaos Emeralds."
        ],
        [
            "THE COBALT EXPLOSION",
            "",
            "To help the doctor test his theories, Sonic trained on an advanced treadmill.",
            "Sonic pushed his limits and ran so fast that he broke the sound barrier!",
            "The resulting kinetic explosion fused his quills into a permanent cobalt blue.",
            "To protect his feet, Kintobor gifted him his iconic friction-resistant red shoes."
        ],
        [
            "THE BIRTH OF EGGMAN",
            "",
            "One fateful afternoon, a disaster struck. While holding a rotten egg,",
            "Dr. Kintobor tripped into the R.O.C.C. machine during a severe malfunction.",
            "The compressed evil energy fused into his body and corrupted his mind,",
            "transforming the kind scientist into the villainous Dr. Ivo Robotnik (Eggman)!"
        ]
    ]
    
    currentPage = 0
    frameCount = 0
    
    while True:
        frameCount += 1
        mx, my = mouse.get_pos()
        
        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return "menu"
                if e.key == K_SPACE:
                    currentPage += 1
                    if currentPage >= len(pages):
                        return "menu"
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                currentPage += 1
                if currentPage >= len(pages):
                    return "menu"
                    
        screen.blit(menuBgImg, (0, 0))
        
        overlay = Surface((w - 200, h - 250), SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (100, 100))
        
        storyData = pages[currentPage]
        
        lblTitle = titleFont.render(storyData[0], True, yellow)
        screen.blit(lblTitle, (w // 2 - lblTitle.get_width() // 2, 140))
        
        currentY = 240
        for line in storyData[2:]:
            lblLine = bodyFont.render(line, True, white)
            screen.blit(lblLine, (w // 2 - lblLine.get_width() // 2, currentY))
            currentY += 45
            
        pulse = int(127 + 127 * sin(frameCount * 0.07))
        promptColor = (pulse, pulse, pulse)
        
        promptText = "Press spacebar or click to continue..." if currentPage < len(pages) - 1 else "Press SPACEbar to return to Menu..."
        lblPrompt = promptFont.render(promptText, True, promptColor)
        screen.blit(lblPrompt, (w // 2 - lblPrompt.get_width() // 2, h - 210))
        
        lblPageNum = bodyFont.render(f"{currentPage + 1} / {len(pages)}", True, grey)
        screen.blit(lblPageNum, (w // 2 - lblPageNum.get_width() // 2, h - 140))
        
        display.flip()
        c.tick(60)

def instructionsScreen():
    c = time.Clock()
    
    titleFont = font.Font("font.otf", 36)
    bodyFont  = font.Font("font.otf", 20)
    promptFont = font.Font("font.otf", 14)
    
    controls = [
        ["LEFT / RIGHT ARROWS", "Move Sonic left and right"],
        ["SPACEBAR / UP ARROW", "Jump / Attack enemies from above"],
        ["X KEY", "Toggle Roll / Spin Dash on the ground"],
        ["ESCAPE KEY", "Return to main menu during gameplay"]
    ]
    
    frameCount = 0
    
    while True:
        frameCount += 1
        
        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return "menu"
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                return "menu"
                
        screen.blit(menuBgImg, (0, 0))
        
        overlay = Surface((w - 200, h - 250), SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (100, 100))
        
        lblTitle = titleFont.render("HOW TO PLAY", True, yellow)
        screen.blit(lblTitle, (w // 2 - lblTitle.get_width() // 2, 140))
        
        currentY = 260
        for key_bind, action in controls:
            lblKey = bodyFont.render(key_bind, True, lightBlue)
            screen.blit(lblKey, (160, currentY))
            
            lblAction = bodyFont.render(f"- {action}", True, white)
            screen.blit(lblAction, (480, currentY))
            
            currentY += 60
            
        lblTipTitle = bodyFont.render("GAMEPLAY TIP:", True, orange)
        screen.blit(lblTipTitle, (160, currentY + 20))
        
        lblTip = bodyFont.render("Roll into enemies or jump on them to destroy them!", True, white)
        screen.blit(lblTip, (160, currentY + 60))
        
        pulse = int(127 + 127 * sin(frameCount * 0.07))
        promptColor = (pulse, pulse, pulse)
        
        lblPrompt = promptFont.render("Press ESCAPE or CLICK to return to menu", True, promptColor)
        screen.blit(lblPrompt, (w // 2 - lblPrompt.get_width() // 2, h - 180))
        
        display.flip()
        c.tick(60)
def mainMenu():
    c = time.Clock()
    
    rawMenuBg = image.load("pics/sonicmenu.png")
    imgW, imgH = rawMenuBg.get_size()
    scale = max(w / imgW, h / imgH)
    scaledW = int(imgW * scale)
    scaledH = int(imgH * scale)
    menuBg = transform.scale(rawMenuBg, (scaledW, scaledH))
    menuBgOffsetX = (scaledW - w) // 2
    menuBgOffsetY = (scaledH - h) // 2
    
    btnStart        = Rect(w // 2 - 315, h - 240, 600, 60)
    btnStory        = Rect(w // 2 - 315, h - 160, 600, 60)
    btnInstructions = Rect(w // 2 - 315, h - 80, 600, 60)
    
    menuFont = font.Font("font.otf", 36)
    
    gold = (255, 215, 0)
    whiteColor = (255, 255, 255)
    black = (0, 0, 0)

    def renderCenteredTextWithOutline(text, font_obj, text_color, outline_color, rect):
        base = font_obj.render(text, True, text_color)
        outline = font_obj.render(text, True, outline_color)
        
        x = rect.x + (rect.width - base.get_width()) // 2
        y = rect.y + (rect.height - base.get_height()) // 2
        
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    screen.blit(outline, (x + dx, y + dy))
        screen.blit(base, (x, y))

    while True:
        screen.blit(menuBg, (-menuBgOffsetX, -menuBgOffsetY))
        mx, my = mouse.get_pos()

        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if btnStart.collidepoint(mx, my):
                    return "play"
                if btnStory.collidepoint(mx, my):
                    return "story"
                if btnInstructions.collidepoint(mx, my):
                    return "instructions"

        colorStart = whiteColor if btnStart.collidepoint(mx, my) else gold
        colorStory = whiteColor if btnStory.collidepoint(mx, my) else gold
        colorInst  = whiteColor if btnInstructions.collidepoint(mx, my) else gold

        renderCenteredTextWithOutline("START", menuFont, colorStart, black, btnStart)
        renderCenteredTextWithOutline("STORY", menuFont, colorStory, black, btnStory)
        renderCenteredTextWithOutline("INSTRUCTIONS", menuFont, colorInst, black, btnInstructions)

        display.flip()
        c.tick(60)
    while True:
        screen.fill(grey)
        mx, my = mouse.get_pos()

        for e in event.get():
            if e.type == QUIT:
                return "exit"
            if e.type == MOUSEBUTTONDOWN:
                if btnStart.collidepoint(mx, my):
                    return "play"
                if btnStory.collidepoint(mx, my):
                    return "story"
                if btnInstructions.collidepoint(mx, my):
                    return "instructions"

        for btn in [btnStart, btnStory, btnInstructions]:
            draw.rect(screen, blue, btn)

        screen.blit(f.render("START",        True, white), (155, 110))
        screen.blit(f.render("STORY",        True, white), (155, 210))
        screen.blit(f.render("INSTRUCTIONS", True, white), (108, 310))

        display.flip()
        c.tick(60)
def fixMapClipping(p, vel, cam, isJumping):
    # Get the exact pixel position of Sonic's middle-feet on the screen canvas
    sx = int(p[X] - cam[0] + (p[W] / 2))
    sy = int(p[Y] - cam[1] + p[H])
    
    # If he's off-screen horizontally, don't check
    if sx < 0 or sx >= w:
        return isJumping
        
    # Check a 60-pixel tall safety zone ABOVE his feet 
    # This catches him if he teleports entirely past the line in one frame
    for check_y in range(sy - 60, sy + 5):
        if 0 <= check_y < h:
            pixel_color = screen.get_at((sx, check_y))[:3]
            
            # If we find your exact brown platform line color
            if pixel_color[0] == 69 and pixel_color[1] == 23 and pixel_color[2] == 0:
                # Convert the screen coordinate back to the global map Y coordinate
                actual_ground_y = check_y + cam[1]
                
                # Snap Sonic safely on top of it
                p[Y] = actual_ground_y - 50 - p[H]
                vel[1] = 0
                return False  # He is no longer jumping, he landed!
                
    return isJumping
def playLevel():
    c = time.Clock()
    p   = [200, 100, 80, 80, 0, 0]
    vel = [0, 0]
    cam = [0, 0]

    isJumping     = False
    isRolling     = False
    xPressedLast  = False
    rollFrame     = 0.0
    invincibility = 0
    powerTimer    = 0

    coinCount   = 0
    lives       = 3
    elapsedTime = 0.0
    score       = 0
    comboKills  = 0

    coins = [
        [350,  400, 40, 40, 0.0, False],
        [1000, 400, 40, 40, 0.0, False],
        [1060, 400, 40, 40, 0.0, False],
    ]

    enemies = [
        [7917, 264, 140, 100, 7717, 8117, 2, 0.0],
        [7923, 264, 140, 100, 7723, 8123, 2, 0.0],
    ]

    fishes = [
        [4078, 496, 100, 100, False, 0.0, 496, 60, 0.0],
        [4078, 496, 100, 100, False, 0.0, 496, 60, 0.0],
        [9585,  97, 100, 100, False, 0.0,  97, 60, 0.0],
        [9873,  95, 100, 100, False, 0.0,  95, 60, 0.0],
    ]

    bombers = [
        [8555,  -24, 110, 80,  8355,  8755, 2, 0, False, 0.0],
        [3702,  167, 110, 80,  3502,  3902, 2, 0, False, 0.0],
        [5307,   96, 110, 80,  5107,  5507, 2, 0, False, 0.0],
        [12598, -520, 110, 80, 12398, 12798, 2, 0, False, 0.0],
        [12081, -549, 110, 80, 11881, 12281, 2, 0, False, 0.0],
        [17936, -1664, 110, 80, 17736, 18136, 2, 0, False, 0.0],
    ]

    projectiles  = []
    droppedCoins = []

    winBox  = [2600, 350, 100, 100]
    jumpPads = [
        [19253, -1397, 120, 80, False, 0],
        [20171, -1667, 120, 80, False, 0],
        [2888,   152,  120, 80, False, 0],
        [12957,  -476, 120, 80, False, 0],
    ]

    monitor = [17420, -1451, 60, 60, False]
    star    = [0.0, 0.0, False, 0.0]

    while True:
        for e in event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                return "menu"

        if lives <= 0:
            # --- PLAY LOSE MUSIC ONLY ON GAME OVER ---
            mixer.music.load("lose.mp3")
            mixer.music.play()

            gameOverStart = time.get_ticks()
            fLarge = font.SysFont(None, 120)
            while time.get_ticks() - gameOverStart < 3000:
                for e in event.get():
                    if e.type == QUIT:
                        return "exit"
                screen.fill((0, 0, 0))
                txt = fLarge.render("GAME OVER!", True, red)
                screen.blit(txt, (w // 2 - txt.get_width() // 2, h // 2 - txt.get_height() // 2))
                display.flip()
            return "menu"

        elapsedTime += 1.0 / 60.0
        if powerTimer > 0:
            powerTimer -= 1

        godMode = powerTimer > 0

        isJumping, isRolling, xPressedLast, rollFrame = handleInput(p, vel, isJumping, invincibility, isRolling, xPressedLast, rollFrame)
        isJumping, invincibility, fallDeath, isRolling = updatePhysics(p, vel, cam, isJumping, invincibility, isRolling)

        if fallDeath == True:
            lives     -= 1
            powerTimer = 0

        updateCoins(coins)
        updateEnemies(cam, enemies, p)
        updateFishEnemies(fishes)
        updateBuzzBombers(bombers, p, projectiles)
        projectiles  = updateProjectiles(projectiles)
        droppedCoins = updateDroppedCoins(cam, droppedCoins)

        prevCoinCount = coinCount
        coinCount = checkCoinCollect(p, coinCount, coins)
        coinCount, droppedCoins = collectDroppedCoins(p, coinCount, droppedCoins)
        score += (coinCount - prevCoinCount) * 100
        prevEnemyCount = len(enemies) + len(fishes) + len(bombers)
        invincibility, coinCount, lives = checkEnemyCollision(
            p, vel, invincibility, coinCount, lives, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, godMode
        )
        killsThisFrame = prevEnemyCount - (len(enemies) + len(fishes) + len(bombers))
        if killsThisFrame > 0:
            comboKills += killsThisFrame
            killPoints = [100, 200, 500, 1000]
            for _ in range(killsThisFrame):
                idx = min(comboKills - 1, len(killPoints) - 1)
                score += killPoints[idx]
        else:
            if vel[1] == 0:
                comboKills = 0
# ... your enemy updates and movement codes are here ...

        # --- CALL THE SAFETY NET HERE ---
        isJumping = fixMapClipping(p, vel, cam, isJumping)


        # ... your jumpPad, monitors, and render function are down here ...
        playerRect = Rect(p[X], p[Y], p[W], p[H])

        for jumpPad in jumpPads:
            if jumpPad[4] == True:
                jumpPad[5] -= 1
                if jumpPad[5] <= 0:
                    jumpPad[4] = False

            if playerRect.colliderect(Rect(jumpPad[0], jumpPad[1], jumpPad[2], jumpPad[3])):
                vel[1]    = -32
                isJumping = True
                isRolling = False
                p[ROW]    = 3
                p[COL]    = 0
                jumpPad[4] = True
                jumpPad[5] = 15

        if monitor[4] == False:
            if playerRect.colliderect(Rect(monitor[0], monitor[1], monitor[2], monitor[3])):
                monitor[4] = True
                star[0] = monitor[0] + 30
                star[1] = monitor[1] + 10
                star[2] = True
                star[3] = monitor[1] - 50

        if star[2] == True:
            if star[1] > star[3]:
                star[1] -= 2.0

        if star[2] == True:
            starDist = sqrt((p[X] + p[W]//2 - star[0])**2 + (p[Y] + p[H]//2 - star[1])**2)
            if starDist < 55:
                star[2]    = False
                powerTimer = 1200

        if playerRect.colliderect(Rect(winBox[0], winBox[1], winBox[2], winBox[3])):
            return drawVictoryScreen(elapsedTime, score)

        render(p, cam, coinCount, lives, invincibility, coins, enemies, fishes, bombers, projectiles, droppedCoins, isRolling, elapsedTime, winBox, jumpPads, monitor, star, powerTimer, rollFrame, vel, score)

        display.flip()
        c.tick(60)

# --- Main Game State Director Loop ---
current = "menu"
current_bgm = ""

while current != "exit":
    # 1. Menu, Story, or Instructions track handling
    if current in ["menu", "story", "instructions"]:
        if current_bgm != "title":
            mixer.music.load("title.mp3")
            mixer.music.play(-1) # -1 loops it indefinitely
            current_bgm = "title"

    # 2. Level track handling
    elif current == "play":
        if current_bgm != "greenhill":
            mixer.music.load("greenhill.mp3")
            mixer.music.play(-1) # -1 loops it indefinitely
            current_bgm = "greenhill"

    # Execute Screen Functions
    if current == "menu":
        current = mainMenu()
    elif current == "play":
        current = playLevel()
        current_bgm = "" # Reset reference so music switches back to menu title tracks cleanly
    elif current == "story":
        current = storyScreen()
    elif current == "instructions":
        current = instructionsScreen()

quit()
