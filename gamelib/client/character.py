import pyglet
import board

from math import cos, sin, atan2, sqrt
from pyglet.window import key
from sprite import AnimatedSprite

class Character(AnimatedSprite):
    def __init__(self):
        img = pyglet.image.load('../../data/person1.png')
        image_grid = pyglet.image.ImageGrid(img, 4, 4)

        self.moveToX = 0
        self.moveToY = 0

        #self.direction = board.SOUTH
        self.frame_duration = 0.20

        AnimatedSprite.__init__(self,
            image_grid.get_animation(self.frame_duration))

        self.moveSegments = []
        self.currentSegment = 0

        self.walkSpeed = 100

        #self.walkSouth()
        #self.rest()

    def walk(self, moveSegments):
        assert moveSegments
        self.currentSegment = 0
        self.moveSegments = moveSegments

        self.moveToX, self.moveToY = moveSegments[0]
        self.walkSouth()

        pyglet.clock.schedule(self.update)

    def walkNorth(self):
        self.play()
        self.set_loop(0, 4)

    def walkEast(self):
        self.play()
        self.set_loop(4, 8)

    def walkWest(self):
        self.play()
        self.set_loop(8, 12)

    def walkSouth(self):
        self.play()
        self.set_loop(12, 16)

    def rest(self):
        self.set_frame(14)
        self.pause()

    def update(self, dt):
        opp = self.moveToX - self.x
        adj = self.moveToY - self.y

        rad = atan2(opp, adj)

        self.x += self.walkSpeed * dt * sin(rad)
        self.y += self.walkSpeed * dt * cos(rad)

        distance = sqrt(pow(self.moveToX - self.x, 2) + \
                        pow(self.moveToY - self.y, 2))

        if distance <= 3:
            self.currentSegment += 1
            if self.currentSegment >= len(self.moveSegments):
                self.x = self.moveToX
                self.y = self.moveToY
                print "finished!"
                self.rest()
                pyglet.clock.unschedule(self.update)
                return
            print "new segment"
            self.oldMoveToX, self.oldMoveToY = (self.moveToX, self.moveToY)
            self.moveToX, self.moveToY = self.moveSegments[self.currentSegment]

            if self.moveToX > self.oldMoveToX:
                self.walkEast()
            elif self.moveToX < self.oldMoveToX:
                self.walkWest()
            elif self.moveToY > self.oldMoveToY:
                self.walkNorth()
            elif self.moveToY < self.oldMoveToY:
                self.walkSouth()


    def keyPress(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.walkEast()
        elif symbol == key.LEFT:
            self.walkWest()
        elif symbol == key.UP:
            self.walkNorth()
        elif symbol == key.DOWN:
            self.walkSouth()
        elif symbol == key.SPACE:
            self.rest()

