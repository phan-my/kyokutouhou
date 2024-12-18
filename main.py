from bulletpatterns import *
from mechanics import *
import time
import pygame
import pgzrun
from random import randint
from dataclasses import dataclass

# struct-like object for hitboxes and playground
# stackoverflow-35988
@dataclass
class Rectangle:
    xMargins: (int, int)
    yMargins: (int, int)
    xBorders: (int, int)
    yBorders: (int, int)
    """
    tl: (int, int)
    tr: (int, int)
    br: (int, int)
    bl: (int, int)
    """

""" The types of hitboxes.
    (P)layer
        - vulnerable to badboxes
    (PB)PlayerBullets
        - attacks enemies
    (G)oodbox
        - heals player
    (B)adbox
        - attacks player
        - 2 subtypes:
        Enemy
            - vulnerable to player bullets
        Bullets
            - attack player
    (S)tage
        - inert
"""


# set up interface
TITLE = "Kyokutouhou"
WIDTH = 800
HEIGHT = 600
background = Actor("proportional-background")

# set up player
player = Actor("reimu")
playerWidth = 32
playerHeight = 64

# set up scene
# margins and borders are constants as seen in assets/background.xcf
playgroundImage = Actor("playground")
playground = Rectangle(
    (50 + playerWidth/2, 470 - playerWidth/2),
    (30 + playerHeight/2, 560 - playerHeight/2),
    (50, 470),
    (30, 560)
)

playgroundWidth = playground.xMargins[1] - playground.xMargins[0]
playgroundHeight = playground.yMargins[1] - playground.yMargins[0]

playerHitbox = Rectangle(
    (player.x, player.x),
    (player.y, player.y),
    (player.x - playerWidth/2, player.x + playerWidth/2),
    (player.y - playerHeight/2, player.y + playerHeight/2),
)

menu = Rectangle(
    (490, 750),
    (30, 560),
    (490 - 2, 750 + 2),
    (30 - 2, 560 + 2)
)

menuWidth = menu.xMargins[1] - menu.xMargins[0]
menuHeight = menu.yMargins[1] - menu.yMargins[0]
menuBackground = Actor("menu")

# position player
player.x = playground.xMargins[0] + (playgroundWidth/2)
player.y = playground.yMargins[1] - 24

# set up player's shots
PlayerBullets = []
playerBulletCount = 16
playerBulletWidth = 6
playerBulletHeight = 12
playerHealth = 4
playerLevel = 1
nthPlayerBullet = 0
invincibilityFrames = 100

for i in range(playerBulletCount):
    PlayerBullets.append(Actor("1x1"))
    PlayerBullets[i].pos = player.pos

# extras from goodboxes
plusC = Actor("1x1")
plusC.x = menu.xMargins[1] - 50
plusC.y = 250

# set up bullets
Bullets = []
bulletCount = int(1024*2**(0))
bulletWidth = 6
bulletHeight = 12
nthBullet = 0

for i in range(bulletCount):
    Bullets.append(Actor("1x1"))
    Bullets[i].x = randint(playground.xBorders[0], playground.xBorders[1])

# set up enemy
Enemies = []
enemyCount = 128
enemySpeed = 2
nthEnemy = 0
enemy01Width = 32
enemy01Height = 32

for i in range(enemyCount):
    Enemies.append(Actor("1x1"))
    Enemies[i].x = randint(playground.xBorders[0], playground.xBorders[1])
    Enemies[i].y = -enemy01Height

# set up boss
boss = Actor("boss")
bossWidth = 32
bossHeight = 64
boss.x = playground.xMargins[0] + (playgroundWidth/2)
boss.y = bossHeight + int(bossHeight*0.1)
bossHealth = 1024

# badbox (enemy hitbox)
badHitboxCount = bulletCount + enemyCount
BadHitbox = []
for bullet in Bullets:
    BadHitbox.append(bullet)

for enemy01 in Enemies:
    BadHitbox.append(enemyCount)

# set up healing peppers
pepperCount = 8
pepperWidth = 30
pepperHeight = 32
nthPepper = 0
Peppers = []

for i in range(pepperCount):
    Peppers.append(Actor("1x1"))
    Peppers[i].x = randint(playground.xBorders[0], playground.xBorders[1])

# overlay
Hearts = []
for i in range(playerHealth):
    Hearts.append(Actor("heart"))
for i in range(playerHealth):
    Hearts[i].x = menu.xMargins[0] + 50 + (i*(menuWidth - 50))/(playerHealth)
    Hearts[i].y = 200

frame = Actor("frame")

# draw all backgrounds, entities, and overlays
def draw():
    background.draw()
    playgroundImage.draw()
    menuBackground.draw()
    player.draw()
    plusC.draw()

    # https://electronstudio.github.io/pygame-zero-book/chapters/shooter.html
    for bullet in Bullets:
        bullet.draw()
    
    for enemy in Enemies:
        enemy.draw()
    
    for playerBullet in PlayerBullets:
        playerBullet.draw()

    for pepper in Peppers:
        pepper.draw()
    
    boss.draw()

    for heart in Hearts:
        heart.draw()
    
    # draw frame of screen to hide bullets
    frame.draw()

# timing
startLevel = time.time()
timeSinceStart_s = time.time() - startLevel
ticksSinceStart = 0
ticksSincePlayerShot = 0
startFight = time.time()
timeSinceFight_s = time.time()

# "ticks" refer to dt
def update(dt):
    global player, playerHealth, playerLevel, invincibilityFrames
    global enemySpeed, Enemies, enemyCount, nthEnemy, enemy01Width, enemy01Height
    global playerBulletWidth, playerBulletHeight, nthPlayerBullet, ticksSincePlayerShot
    global nthBullet
    global bossHealth
    global nthPepper, nthPepper, pepperWidth, pepperHeight
    global startLevel, ticksSinceStart, timeSinceStart_s, startFight, timeSinceFight_s
    
    """UNIVERSAL MECHANICS"""
    # player mechanics
    movement(player, playground)

    # get timing for shooting function
    if keyboard.z:
        ticksSincePlayerShot += 1
    if not keyboard.z:
        ticksSincePlayerShot = 0
    
    # if statement prevents startshot
    if ticksSinceStart != 0:
        # shooting bullets
        nthPlayerBullet = shooting(PlayerBullets, playerBulletCount, nthPlayerBullet, player, ticksSincePlayerShot)
    
    # killing enemies
    enemy_death(Enemies, enemy01Width, enemy01Height, PlayerBullets)

    # healing pepper mechanics
    for i in range(pepperCount):
        if Peppers[i].x - pepperWidth/2 < player.x < Peppers[i].x + pepperWidth/2 and\
        Peppers[i].y - pepperHeight/2 < player.y < Peppers[i].y + pepperHeight/2 and\
        Peppers[i].image != "1x1":
            Peppers[i].image = "1x1"
            playerHealth += 1
            plusC.image = "plus-c"
    
    # damaging boss
    bossHealth = boss_damage(boss, bossWidth, bossHeight, bossHealth, PlayerBullets)
    
    # win
    if bossHealth <= 0:
        print("???: Oouuuuuch!")
        print("You win!")
        exit()
    
    # playerDies statement as a union of all possible causes of death
    playerDiesToBullet = playerHealth > death(Bullets, bulletCount, bulletWidth, bulletHeight, player, playerHealth)
    playerDiesToEnemy01 = playerHealth > death(Enemies, enemyCount, enemy01Width, enemy01Height, player, playerHealth)
    playerDies = playerDiesToBullet or playerDiesToEnemy01

    # sequence of actions when player dies
    if playerDies and invincibilityFrames < 0:
        # playerHealth-- and reposition player
        playerHealth = death(Bullets, bulletCount, bulletWidth, bulletHeight, player, playerHealth)
        playerHealth = death(Enemies, enemyCount, enemy01Width, enemy01Height, player, playerHealth)
        player.x = playground.xMargins[0] + (playgroundWidth/2)
        player.y = playground.yMargins[1] - 24
        
        if playerHealth < 4:
            Hearts[playerHealth].image = "1x1"
        
        # death sound
        sounds.death.play()
        
        # i-frame mechanics
        invincibilityFrames = 100
    
    # game over
    if playerHealth <= 0:
        print("???: Yay! Now you HAVE to play League!")
        print("\nYou lost at " + str(int(timeSinceFight_s)) + " s")
        exit()
    
    """STAGE PROGRESSION"""
    # part 0: dialogue
    if ticksSinceStart < 1000:
        # skip dialogue option
        if keyboard.lctrl:
            # to trigger dialogue below
            if ticksSinceStart % 10 != 0:
                ticksSinceStart -= ticksSinceStart % 10
            ticksSinceStart += 10
        if ticksSinceStart == 0:
            print("You encounter some weird gremlin.")
            print("???: GoooooD MORNING!!!")
        if ticksSinceStart == 100:
            print("???: Wanna play League?")
        if ticksSinceStart == 300:
            print("Reimu: Are those your hands?")
        if ticksSinceStart == 400:
            print("???: Why, yes, these are my FISTS!")
        if ticksSinceStart == 600:
            print("Reimu: Those perfectly match the holes in our walls.")
        if ticksSinceStart == 800:
            print("    Also, what's League, anyway?")
        if ticksSinceStart == 900:
            print("???: LEAGUE MY BALLS!")
        
        # set timeSinceFight to 0 before fight  
        startFight = time.time()

    # part 1: mediocre random bullets and enemies
    if 1000 <= ticksSinceStart and timeSinceFight_s < 42:
        # for score measurement to not conflict with dialog skipping, using
        # separate timeSinceFight_s (based on startFighr) from timeSinceStart_s
        if ticksSinceStart == 1000:
            startFight = time.time()

            # Built-in Objects
            music.play('to-rizz-the-far-east')
        
        # nth bullet startd falling at 4.5 speed in interval of 2 ticks
        nthBullet = random_straight_bullet(Bullets, bulletCount, nthBullet, "bullet-vertical", playground, 4.5, 2, ticksSinceStart)

        # rare healing pepper
        nthPepper = random_straight_bullet(Peppers, pepperCount, nthPepper, "pepper", playground, 6, randint(1024, 4*1024), ticksSinceStart)
        
        # enemy behavior
        activeEnemies = 16
        nthEnemy = random_enemy01(Enemies, enemyCount, nthEnemy, playground, ticksSinceStart)
    # part 2: double the bullets and enemies
    if timeSinceFight_s > 42:
        if int(timeSinceFight_s) == 43:
            sounds.death.play()
            for bullet in Bullets:
                bullet.image = "1x1"
                bullet.y = 0

        # more frequent bullets
        nthBullet = random_straight_bullet(Bullets, bulletCount, nthBullet, "bullet-vertical", playground, 4.5, 1, ticksSinceStart)
        
        # higher interval
        nthPepper = random_straight_bullet(Peppers, pepperCount, nthPepper, "pepper", playground, 6, randint(1024, 8*1024), ticksSinceStart)

        # enemy behavior
        activeEnemies = 64
        nthEnemy = random_enemy01(Enemies, enemyCount, nthEnemy, playground, ticksSinceStart)


    # update timing variables
    ticksSinceStart += 1
    timeSinceStart_s = time.time() - startLevel
    timeSinceFight_s = time.time() - startFight
    invincibilityFrames -= 1

def main() -> int:
    print("controls")
    print(" arrows - movement")
    print(" shift - slowdown")
    print(" z - shoot\n")
    return 0

if __name__ == 'pgzero.builtins':
    main()

pgzrun.go()
