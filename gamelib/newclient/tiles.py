import pyglet
from pyglet.gl import *

win = pyglet.window.Window(width=1024, height=768)
angle = 0.0

def init():
    glClearColor(0.56, 0.67, 0.77, 0.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

CLOCKWISE = 0
ANTICLOCKWISE = 1

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

class Tile(object):
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y

        self.rotating = True
        self.rotation = 0 # rotation * 90
        self.rotateTo = self.rotation
        self.rotationSpeed = 120
        pyglet.clock.schedule(self.update)

    def rotate(self, direction):
        if not self.rotating:
            pyglet.clock.schedule(self.update)

        self.rotating = True

        if direction == ANTICLOCKWISE:
            if self.rotation + 90 > 360:
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


    def draw(self):
        glPushMatrix()
        glScalef(0.1, 0.1, 0.1)
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.rotation, 0, 0, 1)
        #glTranslatef(self.x, self.y, 0)
        self.vertices.draw(GL_QUADS)
        glPopMatrix()

class TileL(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.vertices = pyglet.graphics.vertex_list(
            60,
            ('v3f', (-2, -2,  0,
                      2, -2,  0,
                      2,  2,  0,
                     -2,  2,  0,

                     -2, -2,  0,
                     -1, -2,  0,
                     -1, -2, .5,
                     -2, -2, .5,

                     -2, -2,  0,
                     -2, -2, .5,
                     -2,  2, .5,
                     -2,  2,  0,

                     -1, -2,  0,
                     -1,  2,  0,
                     -1,  2, .5,
                     -1, -2, .5,

                     -2,  2,  0,
                     -2,  2, .5,
                     -1,  2, .5,
                     -1,  2,  0,

                      1, -2,  0,
                      2, -2,  0,
                      2, -2, .5,
                      1, -2, .5,

                      2, -2,  0,
                      2, -1,  0,
                      2, -1, .5,
                      2, -2, .5,

                      2, -1,  0,
                      1, -1,  0,
                      1, -1, .5,
                      2, -1, .5,

                      1, -2,  0,
                      1, -2, .5,
                      1, -1, .5,
                      1, -1,  0,

                      2,  2,  0,
                     -1,  2,  0,
                     -1,  2, .5,
                      2,  2, .5,

                      2,  2,  0,
                      2,  2, .5,
                      2,  1, .5,
                      2,  1,  0,

                      2,  1,  0,
                      2,  1, .5,
                     -1,  1, .5,
                     -1,  1,  0,

                     -2, -2, .5,
                     -1, -2, .5,
                     -1,  2, .5,
                     -2,  2, .5,

                      2, -2, .5,
                      2, -1, .5,
                      1, -1, .5,
                      1, -2, .5,

                      2,  2, .5,
                     -1,  2, .5,
                     -1,  1, .5,
                      2,  1, .5,

                    )
            ),
            ('c3B', ((252, 182, 83) * 4) +
                    ((140, 209, 157) * 44) +
                    ((206, 232, 121) * 12)
            )
        )

class TileT(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)

        self.vertices = pyglet.graphics.vertex_list(
            64,
            ('v3f', (-2, -2,  0,
                      2, -2,  0,
                      2,  2,  0,
                     -2,  2,  0,

                     -2, -2,  0,
                     -1, -2,  0,
                     -1, -2, .5,
                     -2, -2, .5,

                     -2, -2,  0,
                     -2, -2, .5,
                     -2,  2, .5,
                     -2,  2,  0,

                     -1, -2,  0,
                     -1,  2,  0,
                     -1,  2, .5,
                     -1, -2, .5,

                     -2,  2,  0,
                     -2,  2, .5,
                     -1,  2, .5,
                     -1,  2,  0,

                      1, -2,  0,
                      2, -2,  0,
                      2, -2, .5,
                      1, -2, .5,

                      2, -2,  0,
                      2, -1,  0,
                      2, -1, .5,
                      2, -2, .5,

                      2, -1,  0,
                      1, -1,  0,
                      1, -1, .5,
                      2, -1, .5,

                      1, -2,  0,
                      1, -2, .5,
                      1, -1, .5,
                      1, -1,  0,

                      1,  2,  0,
                      1,  2, .5,
                      2,  2, .5,
                      2,  2,  0,

                      2,  2,  0,
                      2,  2, .5,
                      2,  1, .5,
                      2,  1,  0,

                      2,  1,  0,
                      2,  1, .5,
                      1,  1, .5,
                      1,  1,  0,

                      1,  2,  0,
                      1,  1,  0,
                      1,  1, .5,
                      1,  2, .5,

                     -2, -2, .5,
                     -1, -2, .5,
                     -1,  2, .5,
                     -2,  2, .5,

                      2, -2, .5,
                      2, -1, .5,
                      1, -1, .5,
                      1, -2, .5,

                      2,  2, .5,
                      1,  2, .5,
                      1,  1, .5,
                      2,  1, .5,

                    )
            ),
            ('c3B', ((252, 182, 83) * 4) +
                    ((140, 209, 157) * 48) +
                    ((206, 232, 121) * 12)
            )
        )

class TileI(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.vertices = pyglet.graphics.vertex_list(
            44,
            ('v3f', (-2, -2,  0,
                      2, -2,  0,
                      2,  2,  0,
                     -2,  2,  0,

                     -2, -2,  0,
                     -1, -2,  0,
                     -1, -2, .5,
                     -2, -2, .5,

                     -2, -2,  0,
                     -2, -2, .5,
                     -2,  2, .5,
                     -2,  2,  0,

                     -1, -2,  0,
                     -1,  2,  0,
                     -1,  2, .5,
                     -1, -2, .5,

                     -2,  2,  0,
                     -2,  2, .5,
                     -1,  2, .5,
                     -1,  2,  0,

                      1, -2,  0,
                      2, -2,  0,
                      2, -2, .5,
                      1, -2, .5,

                      2, -2,  0,
                      2,  2,  0,
                      2,  2, .5,
                      2, -2, .5,

                      1, -2,  0,
                      1, -2, .5,
                      1,  2, .5,
                      1,  2,  0,

                      2,  2,  0,
                      1,  2,  0,
                      1,  2, .5,
                      2,  2, .5,

                     -2, -2, .5,
                     -1, -2, .5,
                     -1,  2, .5,
                     -2,  2, .5,

                      2, -2, .5,
                      2,  2, .5,
                      1,  2, .5,
                      1, -2, .5,

                    )
            ),
            ('c3B', ((252, 182, 83) * 4) +
                    ((140, 209, 157) * 32) +
                    ((206, 232, 121) * 8)
            )
        )

sel = 0

tiles = [
    TileT(4, 4),
    TileL(0, 4),
    TileI(-4, 4),
    TileT(4, 0),
    TileI(0, 0),
    TileL(-4, 0),
    TileL(4, -4),
    TileT(0, -4),
    TileI(-4, -4)
]

@win.event
def on_draw():
    win.clear()

    glLoadIdentity()

    glPolygonMode(GL_FRONT, GL_FILL)
    glColor4f(1, 1, 1, 1)

    glRotatef(-30, 1, 0, 0)
    [tile.draw() for tile in tiles]

@win.event
def on_key_release(symbol, modifiers):
    global sel
    if symbol == pyglet.window.key.RIGHT:
        tiles[sel].rotate(CLOCKWISE)
    elif symbol == pyglet.window.key.LEFT:
        tiles[sel].rotate(ANTICLOCKWISE)
    elif symbol == pyglet.window.key.UP:
        sel -= 1
        if sel < 0:
            sel = len(tiles) - 1
    elif symbol == pyglet.window.key.DOWN:
        sel += 1
        if sel >= len(tiles):
            sel = 0
    

def update(dt):
    global angle
    angle += 0.2

init()

pyglet.clock.schedule(update)
pyglet.app.run()

