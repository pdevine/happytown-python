import pyglet
from pyglet.gl import *
import random

from math import sin, cos, radians, atan2, sqrt, log

CLOCKWISE = 0
ANTICLOCKWISE = 1

BOARD_SMALL = 0.2
BOARD_MEDIUM = 0.06
BOARD_LARGE = 0.055
BOARD_HUGE = 0.03

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

class TileManager(object):
    def __init__(self, rows, columns, tileScale=BOARD_SMALL):
        self.rows = rows
        self.columns = columns

        self.scale = tileScale

        self.moving = False

        self.tiles = []

        startX = columns * Tile.width / 2
        startY = rows * Tile.height / 2

        tileChoices = [TileI, TileT, TileL]

        self.rowPositions = \
            range(startY - Tile.height / 2, -startY, -Tile.height)
        self.columnPositions = \
            range(-startX + Tile.width / 2, startX, Tile.width)

        for y in self.rowPositions:
            for x in self.columnPositions:
                print "%d, %d" % (x, y)
                rotation = random.randint(0, 3)
                tile = random.choice(tileChoices)
                self.tiles.append(tile(x, y, tileScale, rotation))

        tileType = random.choice(tileChoices)

        self.floatingTile = \
            tileType(-100, -100, tileScale, random.randint(0, 3))

    def moveTiles(self, position, direction):
        assert direction in [NORTH, EAST, SOUTH, WEST]
        assert self.moving == False

        self.moving = True
        self.movingTiles = []
        self.tilePushed = True

        if direction in [EAST, WEST]:
            for tile in self.tiles:
                if self.rowPositions.index(tile.y) == position:
                    self.movingTiles.append(tile)

            # the tiles have to be in order to find the correct floating tile
            self.movingTiles.sort(lambda tile1, tile2: cmp(tile1.x, tile2.x))

            if direction == EAST:
                tile = self.movingTiles[0]
                self.floatingTile.x = tile.x - Tile.width
                self.floatingTile.y = tile.y
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y

                self.movingTiles.insert(0, self.floatingTile)
                self.tiles.append(self.floatingTile)

                self.floatingTile = self.movingTiles[-1]
                self.tiles.remove(self.floatingTile)

                for tile in self.movingTiles:
                    tile.moveToX = tile.x + Tile.width

            pyglet.clock.schedule(self.update)

    def on_mouse_release(self, x, y, button, modifiers):
        glLoadIdentity()

        model = (GLdouble * 16)()
        projection = (GLdouble * 16)()
        viewport = (GLint * 4)()

        glGetDoublev(GL_MODELVIEW_MATRIX, model)
        glGetDoublev(GL_PROJECTION_MATRIX, projection)
        glGetIntegerv(GL_VIEWPORT, viewport)

        objX = GLdouble()
        objY = GLdouble()
        objZ = GLdouble()

        gluUnProject(x, y, 10.0, model, projection, viewport, objX, objY, objZ)

        pointX = objX.value * 1 / self.scale
        pointY = objY.value * 1 / self.scale

        print "(%f, %f, %f)" % (objX.value * 1 / self.scale, objY.value * 1 / self.scale, objZ.value)

        for tile in self.tiles:
            if tile.collidePoint(pointX, pointY):
                print tile
                break

        print "release!"

    def update(self, dt):
        if self.moving:
            for tile in self.movingTiles:
                opp = tile.moveToX - tile.x
                adj = tile.moveToY - tile.y

                rad = atan2(opp, adj)

                deltaX = tile.moveSpeed * dt * sin(rad)
                deltaY = tile.moveSpeed * dt * cos(rad)

                distance = sqrt((tile.moveToX - tile.x) ** 2 +
                                (tile.moveToY - tile.y) ** 2)

                if distance <= 0.05:
                    tile.x = tile.moveToX
                    tile.y = tile.moveToY
                    self.movingTiles.remove(tile)
                    continue
                elif distance < 0.75:
                    braking = log(distance + 10, 10) - 1
                    deltaX *= braking * 30
                    deltaY *= braking * 10

                tile.x += deltaX
                tile.y += deltaY 

        if not self.movingTiles:
            self.moving = False
            pyglet.clock.unschedule(self.update)

    def draw(self):
        for tile in self.tiles:
            tile.draw()

        self.floatingTile.draw()

class Tile(object):
    width = 4
    height = 4

    def __init__(self, x, y, scale=BOARD_MEDIUM, rotation=0):
        self.x = x
        self.y = y

        self.moveToX = self.x
        self.moveToY = self.y

        self.scale = scale

        self.moveSpeed = 1.5

        self.rotating = True
        self.rotation = rotation * 90
        self.rotateTo = self.rotation
        self.rotationSpeed = 120
        pyglet.clock.schedule(self.update)

    def collidePoint(self, x, y):
        if x > self.x - self.width / 2 and x < self.x + self.width / 2 and \
           y > self.y - self.height / 2 and y < self.y + self.height / 2:
            return True
        return False

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
        #glScalef(self.scale, self.scale, self.scale)
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.rotation, 0, 0, 1)
        self.vertices.draw(GL_QUADS)
        glPopMatrix()

class TileL(Tile):
    def __init__(self, x, y, scale=BOARD_MEDIUM, rotation=0):
        Tile.__init__(self, x, y, scale, rotation)
        self.vertices = pyglet.graphics.vertex_list(
            60,
            ('v3f', (-2, -2,  0,
                      2, -2,  0,
                      2,  2,  0,
                     -2,  2,  0,

                     -2, -2,  0,
                     -1, -2,  0,
                     -1, -2, .2,
                     -2, -2, .2,

                     -2, -2,  0,
                     -2, -2, .2,
                     -2,  2, .2,
                     -2,  2,  0,

                     -1, -2,  0,
                     -1,  2,  0,
                     -1,  2, .2,
                     -1, -2, .2,

                     -2,  2,  0,
                     -2,  2, .2,
                     -1,  2, .2,
                     -1,  2,  0,

                      1, -2,  0,
                      2, -2,  0,
                      2, -2, .2,
                      1, -2, .2,

                      2, -2,  0,
                      2, -1,  0,
                      2, -1, .2,
                      2, -2, .2,

                      2, -1,  0,
                      1, -1,  0,
                      1, -1, .2,
                      2, -1, .2,

                      1, -2,  0,
                      1, -2, .2,
                      1, -1, .2,
                      1, -1,  0,

                      2,  2,  0,
                     -1,  2,  0,
                     -1,  2, .2,
                      2,  2, .2,

                      2,  2,  0,
                      2,  2, .2,
                      2,  1, .2,
                      2,  1,  0,

                      2,  1,  0,
                      2,  1, .2,
                     -1,  1, .2,
                     -1,  1,  0,

                     -2, -2, .2,
                     -1, -2, .2,
                     -1,  2, .2,
                     -2,  2, .2,

                      2, -2, .2,
                      2, -1, .2,
                      1, -1, .2,
                      1, -2, .2,

                      2,  2, .2,
                     -1,  2, .2,
                     -1,  1, .2,
                      2,  1, .2,

                    )
            ),
            ('c3B', ((252, 182, 83) * 4) +
                    ((140, 209, 157) * 44) +
                    ((206, 232, 121) * 12)
            )
        )

class TileT(Tile):
    def __init__(self, x, y, scale=BOARD_MEDIUM, rotation=0):
        Tile.__init__(self, x, y, scale, rotation)

        self.vertices = pyglet.graphics.vertex_list(
            64,
            ('v3f', (-2, -2,  0,
                      2, -2,  0,
                      2,  2,  0,
                     -2,  2,  0,

                     -2, -2,  0,
                     -1, -2,  0,
                     -1, -2, .2,
                     -2, -2, .2,

                     -2, -2,  0,
                     -2, -2, .2,
                     -2,  2, .2,
                     -2,  2,  0,

                     -1, -2,  0,
                     -1,  2,  0,
                     -1,  2, .2,
                     -1, -2, .2,

                     -2,  2,  0,
                     -2,  2, .2,
                     -1,  2, .2,
                     -1,  2,  0,

                      1, -2,  0,
                      2, -2,  0,
                      2, -2, .2,
                      1, -2, .2,

                      2, -2,  0,
                      2, -1,  0,
                      2, -1, .2,
                      2, -2, .2,

                      2, -1,  0,
                      1, -1,  0,
                      1, -1, .2,
                      2, -1, .2,

                      1, -2,  0,
                      1, -2, .2,
                      1, -1, .2,
                      1, -1,  0,

                      1,  2,  0,
                      1,  2, .2,
                      2,  2, .2,
                      2,  2,  0,

                      2,  2,  0,
                      2,  2, .2,
                      2,  1, .2,
                      2,  1,  0,

                      2,  1,  0,
                      2,  1, .2,
                      1,  1, .2,
                      1,  1,  0,

                      1,  2,  0,
                      1,  1,  0,
                      1,  1, .2,
                      1,  2, .2,

                     -2, -2, .2,
                     -1, -2, .2,
                     -1,  2, .2,
                     -2,  2, .2,

                      2, -2, .2,
                      2, -1, .2,
                      1, -1, .2,
                      1, -2, .2,

                      2,  2, .2,
                      1,  2, .2,
                      1,  1, .2,
                      2,  1, .2,

                    )
            ),
            ('c3B', ((252, 182, 83) * 4) +
                    ((140, 209, 157) * 48) +
                    ((206, 232, 121) * 12)
            )
        )

class TileI(Tile):
    def __init__(self, x, y, scale=BOARD_MEDIUM, rotation=0):
        Tile.__init__(self, x, y, scale, rotation)
        self.vertices = pyglet.graphics.vertex_list(
            44,
            ('v3f', (-2, -2,  0,
                      2, -2,  0,
                      2,  2,  0,
                     -2,  2,  0,

                     -2, -2,  0,
                     -1, -2,  0,
                     -1, -2, .2,
                     -2, -2, .2,

                     -2, -2,  0,
                     -2, -2, .2,
                     -2,  2, .2,
                     -2,  2,  0,

                     -1, -2,  0,
                     -1,  2,  0,
                     -1,  2, .2,
                     -1, -2, .2,

                     -2,  2,  0,
                     -2,  2, .2,
                     -1,  2, .2,
                     -1,  2,  0,

                      1, -2,  0,
                      2, -2,  0,
                      2, -2, .2,
                      1, -2, .2,

                      2, -2,  0,
                      2,  2,  0,
                      2,  2, .2,
                      2, -2, .2,

                      1, -2,  0,
                      1, -2, .2,
                      1,  2, .2,
                      1,  2,  0,

                      2,  2,  0,
                      1,  2,  0,
                      1,  2, .2,
                      2,  2, .2,

                     -2, -2, .2,
                     -1, -2, .2,
                     -1,  2, .2,
                     -2,  2, .2,

                      2, -2, .2,
                      2,  2, .2,
                      1,  2, .2,
                      1, -2, .2,

                    )
            ),
            ('c3B', ((252, 182, 83) * 4) +
                    ((140, 209, 157) * 32) +
                    ((206, 232, 121) * 8)
            )
        )

if __name__ == '__main__':

    win = pyglet.window.Window(width=1024, height=768)

    def init():
        glClearColor(92/255.0, 172/255.0, 196/255.0, 0.0)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    @win.event
    def on_resize(width, height):
        if not height:
            height = 1

        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #glFrustum(-1.0, 1.0, -1.0, 1.0, 1.0, 1000.0)
        glOrtho(-1.0, 1.0, -1.0, 1.0, 1.0, 1000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        return pyglet.event.EVENT_HANDLED

    sel = 0

    tiles = TileManager(4, 4)


    @win.event
    def on_draw():
        win.clear()

        glLoadIdentity()

        gluLookAt(0, -6, 12,
                 0, 50, -100.0,
                 0, 1, 0)

        glScalef(0.1, 0.1, 0.1)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor4f(1, 1, 1, 1)

        tiles.draw()


    win.push_handlers(tiles)

    @win.event
    def on_key_release(symbol, modifiers):

        if symbol == pyglet.window.key.RIGHT:
            tiles.moveTiles(1, EAST)

#        if symbol == pyglet.window.key.RIGHT:
#            tiles[sel].rotate(CLOCKWISE)
#        elif symbol == pyglet.window.key.LEFT:
#            tiles[sel].rotate(ANTICLOCKWISE)
#        elif symbol == pyglet.window.key.UP:
#            sel -= 1
#            if sel < 0:
#                sel = len(tiles) - 1
#        elif symbol == pyglet.window.key.DOWN:
#            sel += 1
#            if sel >= len(tiles):
#                sel = 0


    def update(dt):
        pass

    init()

    pyglet.clock.schedule(update)
    pyglet.app.run()

