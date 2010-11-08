import pyglet
from math import sin, cos, radians, pow, sqrt, atan2, degrees
from pyglet.gl import *

class Actor(object):
    def __init__(self, x, y, scale):
        self.x = x
        self.y = y
        self.scale = scale

        self.moveToX = x
        self.moveToY = y

        self.moveSegments = []
        self.currentSegment = -1

        self.moving = False
        self.turning = False

        self.rotation = 0

        pyglet.clock.schedule(self.update)

    def move(self, moveSegments):
        self.moveSegments = moveSegments
        self.moveToX, self.moveToY = moveSegments[0]

    def update(self, dt):
        pass

    def draw(self):
        glPushMatrix()
        #glScalef(self.scale, self.scale, self.scale)
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.rotation, 0, 0, 1)
        self.vertices.draw(GL_QUADS)
        glPopMatrix()


class Bus(Actor):
    def __init__(self):
        Actor.__init__(self, 0, 0, 0.1)

        self.speed = 4.0

        self.vertices = pyglet.graphics.vertex_list(
            40,
            ('v3f', (
                     -1.2, -.6,  .3,
                      1.2, -.6,  .3,
                      1.2,  .6,  .3,
                     -1.2,  .6,  .3,

                     -1.2, -.6,  .3,
                      1.2, -.6,  .3,
                      1.2, -.6, 1.8,
                     -1.2, -.6, 1.8,
                    
                     -1.2, -.6, 1.8,
                       .8, -.6, 1.8,
                       .8, -.6, 3.3,
                     -1.2, -.6, 3.3,

                     -1.2,  .6,  .3,
                     -1.2,  .6, 1.8,
                      1.2,  .6, 1.8,
                      1.2,  .6,  .3,

                     -1.2,  .6, 1.8,
                     -1.2,  .6, 3.3,
                       .8,  .6, 3.3,
                       .8,  .6, 1.8,

                      1.2, -.6,  .3,
                      1.2,  .6,  .3,
                      1.2,  .6, 1.8,
                      1.2, -.6, 1.8,

                       .8, -.6, 1.8,
                       .8,  .6, 1.8,
                       .8,  .6, 3.3,
                       .8, -.6, 3.3,

                     -1.2, -.6,  .3,
                     -1.2, -.6, 3.3,
                     -1.2,  .6, 3.3,
                     -1.2,  .6,  .3,

                     -1.2, -.6, 3.3,
                       .8, -.6, 3.3,
                       .8,  .6, 3.3,
                     -1.2,  .6, 3.3,

                       .8, -.6, 1.8,
                      1.2, -.6, 1.8,
                      1.2,  .6, 1.8,
                       .8,  .6, 1.8,

                    )
            ),
            ('c3B', ((1, 1, 1) * 4) +
                    ((247, 224, 51) * 16) +
                    ((236, 212, 30) * 12) +
                    ((241, 212, 0) * 8)
            )
        )

    def update(self, dt):
        if self.turning:
            if self.direction > self.rotation:
                print "dir=%d rot=%d" % (self.direction, self.rotation)
                self.rotation += 5
            elif self.direction < self.rotation:
                print "dir=%d rot=%d" % (self.direction, self.rotation)
                self.rotation -= 5

            if self.rotation == self.direction:
                self.turning = False

        else:
            self.x += cos(radians(self.rotation)) * dt * self.speed
            self.y += sin(radians(self.rotation)) * dt * self.speed


        distance = sqrt(pow(self.moveToX - self.x, 2) + \
                        pow(self.moveToY - self.y, 2))

        if distance < 0.1:
            self.x = self.moveToX
            self.y = self.moveToY

            self.currentSegment += 1
            if self.currentSegment >= len(self.moveSegments):
                pyglet.clock.unschedule(self.update)    
            else:
                self.moveToX, self.moveToY = \
                    self.moveSegments[self.currentSegment]
                self.turning = True

                direction = degrees(
                    atan2(self.moveToY - self.y,
                          self.moveToX - self.x))

                if self.rotation == -90 and direction == 180:
                    self.rotation = 270
                elif self.rotation == 180 and direction == -90:
                    self.rotation = -180

                self.direction = direction


if __name__ == '__main__':

    win = pyglet.window.Window(width=1024, height=768)

    def init():
        glClearColor(92/255.0, 172/255.0, 196/255.0, 0.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    @win.event
    def on_resize(width, height):
        if not height:
            height = 1

        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)

        if width <= height:
            glOrtho(-100.0, 100.0,
                    -100.0 * height / width, 100.0 * height / width,
                    -100.0, 100.0)
        else:
            glOrtho(-100.0 * width / height, 100.0 * width / height,
                    -100.0, 100.0,
                    -100.0, 100.0)

        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return pyglet.event.EVENT_HANDLED

    import tiles

    tileList = [
        tiles.TileT(0, 4, 0.1, 1),
        tiles.TileT(4, 4, 0.1, 3),
        tiles.TileT(-4, 4, 0.1, 3),
        tiles.TileT(0, 0, 0.1, 3),
        tiles.TileT(4, 0, 0.1, 1),
        tiles.TileT(-4, 0, 0.1),
    ]
    bus = Bus()
    bus.x = -4
    bus.y = 0
    bus.move([(0, 0), (4, 0), (4, 4), (0, 4), (-4, 4), (-4, 0), (0, 0)])
    #bus.move([(-4, 0), (-4, 4), (0, 4), (4, 4), (4, 0), (0, 0), (-4, 0)])

    @win.event
    def on_key_release(symbol, modifiers):
        if symbol == pyglet.window.key.RIGHT:
            bus.rotation -= 5
        elif symbol == pyglet.window.key.LEFT:
            bus.rotation += 5

    @win.event
    def on_draw():
        win.clear()

        glLoadIdentity()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glColor4f(1, 1, 1, 1)

        glRotatef(-30, 1, 0, 0)

        glScalef(.1, .1, .1)
        for tile in tileList:
            tile.draw()

        bus.draw()

    init()
    pyglet.app.run()

