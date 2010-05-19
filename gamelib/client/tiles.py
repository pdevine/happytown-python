import sys
import pyglet

import random

from random import randint

TILE_IMAGES = [
    '',
    pyglet.image.load('../../data/tile-i3.png'),
    pyglet.image.load('../../data/tile-l3-r.png'),
    pyglet.image.load('../../data/tile-t3.png'),
]

for img in TILE_IMAGES:
    if img:
        img.anchor_x = int(img.width / 2)
        img.anchor_y = int(img.height / 2)

FLOATINGTILE_LOCATION_X = 800
FLOATINGTILE_LOCATION_Y = 650

MOVE_SPEED = 100
SNAP_SPEED = 700

CLOCKWISE = 1
ANTICLOCKWISE = 2


class Tile(pyglet.sprite.Sprite):
    def __init__(self, x, y, column, row, color=(255, 255, 255), tileType=1,
                       tileRotation=0, batch=None):

        pyglet.sprite.Sprite.__init__(self, TILE_IMAGES[tileType], batch=batch)

        self.rotationSpeed = 120

        self.x = x
        self.y = y

        self.row = row
        self.column = column

        self.velocityX = 0
        self.velocityY = 0

        self.moveToX = x
        self.moveToY = y
        self.moveSpeed = MOVE_SPEED

        self.slowDown = True

        self.rotating = False
        self.rotation = tileRotation * 90
        self.rotateTo = self.rotation

        self.falling = False

        self.color = color


    def rotate(self, direction):
        if not self.rotating:
            pyglet.clock.schedule(self.update)

        self.rotating = True

        if direction == CLOCKWISE:
            if self.rotation + 90 >= 360:
                self.rotation -= 360
                self.rotateTo -= 270
            else:
                self.rotateTo += 90
        else:
            if self.rotation - 90 <= 0:
                self.rotation += 360
                self.rotateTo += 270
            else:
                self.rotateTo -= 90

    def getPosition(self):
        return (self.x, self.y)

    def setPosition(self, xy):
        self.x, self.y = xy

    xy = property(getPosition, setPosition)

    def getMovePosition(self):
        return (self.moveToX, self.moveToY)

    def setMovePosition(self, xy):
        self.moveToX, self.moveToY = xy

    moveXY = property(getMovePosition, setMovePosition)

    def reset(self):
        self.x = self.moveToX
        self.y = self.moveToY
        self.moveSpeed = MOVE_SPEED

    def resetFloatingTile(self):
        self.scale = 1
        self.falling = False
        self.moveToX = FLOATINGTILE_LOCATION_X
        self.moveToY = FLOATINGTILE_LOCATION_Y
        self.x = FLOATINGTILE_LOCATION_X
        self.y = FLOATINGTILE_LOCATION_Y

    def update(self, dt):
        if self.rotating:
            if self.rotation < self.rotateTo:
                self.rotation = min(self.rotationSpeed * dt + self.rotation,
                                    self.rotateTo)
            elif self.rotation > self.rotateTo:
                self.rotation = max(self.rotation - self.rotationSpeed * dt,
                                    self.rotateTo)

            if self.rotation == self.rotateTo:
                self.rotating = False
                pyglet.clock.unschedule(self.update)


class Spark:
    lifetimeRange = (150, 450)
    colors = [(255, 0, 0), (255, 255, 100), (255, 255, 0), (10, 10, 10)]

    def __init__(self, pos):
        self.dead = False
        self.color = random.choice(self.colors)

        self.x, self.y = pos
        self.lifetime = 0.01 * randint(*self.lifetimeRange)

        self.velocityX = randint(-2, 2)
        self.velocityY = randint(-3, 1)


    def update(self, tick):
        self.lifetime -= tick
        if self.lifetime <= 0:
            self.dead = True

        self.x += self.velocityX
        self.y += self.velocityY

    def draw(self):
        pyglet.gl.glColor3ub(*self.color)
        pyglet.graphics.draw(2, pyglet.gl.GL_POINTS,
                                ('v2i', (self.x, self.y, self.x+1, self.y)))

class SparkManager:
    def __init__(self, pos):
        self.x, self.y = pos
        self.sparks = []

        self.sparkInterval = 0.20
        self.sparkTimer = self.sparkInterval

        pyglet.clock.schedule(self.update)

    def update(self, tick):
        self.sparkTimer -= tick

        if self.sparkTimer <=0:
            self.sparks.append(Spark((self.x, self.y)))
            self.sparkTimer = self.sparkInterval

        for spark in self.sparks:
            spark.update(tick)

            if spark.dead:
                self.sparks.remove(spark)


    def draw(self):
        pyglet.gl.glPointSize(2.0)

        for spark in self.sparks:
            spark.draw()

        pyglet.gl.glColor3ub(255, 255, 255)

if __name__ == '__main__':
    window = pyglet.window.Window(1024, 768)

    sparks = SparkManager((100, 100))

    @window.event
    def on_draw():
        window.clear()
        sparks.draw()

    pyglet.app.run()


