from bulletpatterns import *
from mechanics import *
import math
from math import cos, fmod
import time
from time import sleep
import pygame
import pgzrun
from random import randint
from dataclasses import dataclass
PI = 3.141592653589793238462643

# struct-like object for hitboxes and playground
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

TITLE = "Kyokutouhou"
WIDTH = 800
HEIGHT = 600

background = Actor("proportional-background")
player = Actor("reimu")
playerWidth = 32
playerHeight = 64

playground = Rectangle(
    (50 + playerWidth/2, 470 - playerWidth/2),
    (30 + playerHeight/2, 560 - playerHeight/2),
    (50, 470),
    (30, 560)
)

playgroundWidth = playground.xMargins[1] - playground.xMargins[0]
playgroundHeight = playground.yMargins[1] - playground.yMargins[0]
player.x = playground.xMargins[0] + (playgroundWidth/2)
player.y = playground.yMargins[1] - 24

playerHitbox = Rectangle(
    (player.x, player.x),
    (player.y, player.y),
    (player.x - playerWidth/2, player.x + playerWidth/2),
    (player.y - playerHeight/2, player.y + playerHeight/2),
)

Bullets = []

bullets = 1024*10

for i in range(bullets):
    Bullets.append(Actor("bullet-vertical.png"))
    Bullets[i].x = randint(playground.xBorders[0], playground.xBorders[1])

bulletWidth = 6
bulletHeight = 12

def draw():
    background.draw()
    player.draw()

    # https://electronstudio.github.io/pygame-zero-book/chapters/shooter.html
    for bullet in Bullets:
        bullet.draw()

i = 0
start = time.time()
end = time.time()
elapsed = end - start

start_level = time.time()
def update(dt):
    global player, bullet, i, start, end, elapsed, start_level
    movement(player, playground)
    reimu_slowdown(player)


    lap = time.time()
    elapsed_lap = lap - start_level


    # clock.schedule_interval(update_straight_bullet, 2.0)
    random_straight_bullet(Bullets, 4.5, playground, elapsed)
    bulletsOnScreen = 1024
    k = 0
    
    death(Bullets, i, player, bulletsOnScreen, bulletWidth, bulletHeight)

    if elapsed >= 50 and i < bullets - 2 - 1:
        # print(elapsed)
        for j in range(bulletsOnScreen):
            Bullets[i+j].x = 9001
        i += bulletsOnScreen
        start = time.time()
        elapsed = 0
    end = time.time()
    elapsed = end - start
    
# clock.schedule(draw_nth_straight_bullet, 0.5)
pgzrun.go()
print("Hello, World!")
