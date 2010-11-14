import pyglet
from pyglet.gl import *
import random

from math import sin, cos, radians, atan2, sqrt, log

CLOCKWISE = 0
ANTICLOCKWISE = 1

BOARD_SMALL = (0.09, 0.09, 0.09)
BOARD_MEDIUM = (0.06, 0.06, 0.06)
BOARD_LARGE = (0.055, 0.055, 0.055)
BOARD_HUGE = (0.03, 0.03, 0.03)

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

POS_START= 0
POS_END = 1


class TileManager(object):
    def __init__(self, rows, columns, tileScale=BOARD_SMALL):
        self.rows = rows
        self.columns = columns

        self.scale = tileScale

        self.dragTile = False
        self.ourTurn = True

        self.tiles = []
        self.movingTiles = []

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
        '''
            push the floating tile and move a column or row

            position    row or column to move
            direction   direction to move in [NORTH, EAST, SOUTH, WEST]

        '''

        assert direction in [NORTH, EAST, SOUTH, WEST]
        assert len(self.movingTiles) == 0

        self.tilePushed = True

        if direction in [EAST, WEST]:
            for tile in self.tiles:
                if self.rowPositions.index(tile.y) == position:
                    self.movingTiles.append(tile)

            # the tiles have to be in order to find the correct floating tile
            self.movingTiles.sort(lambda tile1, tile2: cmp(tile1.x, tile2.x))

            if direction == EAST:
                self.setMoveTilePositions(
                    self.movingTiles[0], -Tile.width, 0, POS_START)
            elif direction == WEST:
                self.setMoveTilePositions(
                    self.movingTiles[-1], Tile.width, 0, POS_END)

        elif direction in [NORTH, SOUTH]:
            for tile in self.tiles:
                if self.rowPositions.index(tile.x) == position:
                    self.movingTiles.append(tile)

            self.movingTiles.sort(lambda tile1, tile2: cmp(tile2.y, tile1.y))

            if direction == NORTH:
                self.setMoveTilePositions(
                    self.movingTiles[-1], 0, -Tile.height, POS_END)
            elif direction == SOUTH:
                self.setMoveTilePositions(
                    self.movingTiles[0], 0, Tile.height, POS_START)

        pyglet.clock.schedule(self.update)

    def setMoveTilePositions(self, tile, xOffset, yOffset, position):
        '''
            set the floating tile and build up an array of tiles
            to be moved

            tile        tile next to where the floating tile is being pushed
            xOffset     x offset next to the floating tile
            yOffset     y offset next to the floating tile
            position    row or column to push

        '''
        self.floatingTile.x = tile.x + xOffset
        self.floatingTile.y = tile.y + yOffset
        self.floatingTile.moveToX = tile.x
        self.floatingTile.moveToY = tile.y

        if position == POS_START:
            self.movingTiles.insert(0, self.floatingTile)
        else:
            self.movingTiles.append(self.floatingTile)

        self.tiles.append(self.floatingTile)

        if position == POS_START:
            self.floatingTile = self.movingTiles[-1]
        else:
            self.floatingTile = self.movingTiles[0]

        self.tiles.remove(self.floatingTile)

        for tile in self.movingTiles:
            tile.moveToX = tile.x - xOffset
            tile.moveToY = tile.y - yOffset

    def getWorldPointAtWindowPoint(self, x, y):
        '''
            return world coordinates for a given window point
        '''
        glLoadIdentity()

        gluLookAt(0, -6, 12,
                  0, 50, -100.0,
                  0,  1, 0)

        glScalef(*self.scale)

        z = (GLfloat * 1)(0)
        glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, z)

        model = (GLdouble * 16)()
        projection = (GLdouble * 16)()
        viewport = (GLint * 4)()

        glGetDoublev(GL_MODELVIEW_MATRIX, model)
        glGetDoublev(GL_PROJECTION_MATRIX, projection)
        glGetIntegerv(GL_VIEWPORT, viewport)

        objX = GLdouble()
        objY = GLdouble()
        objZ = GLdouble()

        gluUnProject(x, y, z[0], model, projection, viewport, objX, objY, objZ)

        pointX = objX.value
        pointY = objY.value

        return (objX.value, objY.value, objZ.value)

    def getTileAtColumnRow(self, column, row):
        '''return a tile at a board position'''
        return self.getTileAtPoint(
            self.columnPositions[column],
            self.rowPositions[row])

    def getTileAtPoint(self, x, y):
        '''return a tile at world point'''
        for tile in self.tiles:
            if tile.collidePoint(x, y):
                return tile
        return None

    def pickupFloatingTile(self, x, y):
        '''pick up floating tile at world point'''
        if self.floatingTile.collidePoint(x, y):
            self.dragTile = True

    def dropFloatingTile(self, x, y):
        '''drop the floating tile'''

        # TODO - add board movement

        self.movingTiles.append(self.floatingTile)
        self.floatingTile.moveToX = 10
        self.floatingTile.moveToY = 10
        self.floatingTile.moveSpeed = 20
        pyglet.clock.schedule(self.update)

    def pathToCoords(self, movePath):
        '''
            convert a list of board coordinate tuples to world coordinate tuples

            movePath    list of board coordinate (column, row) tuples

        '''
        moveCoords = []
        for column, row in movePath:
            tile = self.getTileAtColumnRow(column, row)
            assert tile
            moveCoords.append((tile.x, tile.y))

        return moveCoords

    def on_mouse_press(self, x, y, button, modifiers):
        if self.ourTurn:
            wx, wy, wz = self.getWorldPointAtWindowPoint(x, y)
            self.pickupFloatingTile(wx, wy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragTile:
            wx, wy, wz = self.getWorldPointAtWindowPoint(x, y)
            self.floatingTile.x = wx
            self.floatingTile.y = wy

    def on_mouse_release(self, x, y, button, modifiers):
        if self.ourTurn:
            wx, wy, wz = self.getWorldPointAtWindowPoint(x, y)
            tile = self.getTileAtPoint(wx, wy)
            if self.dragTile:
                self.dropFloatingTile(wx, wy)
        print tile

    def update(self, dt):
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
                tile.moveSpeed = 1.5
                self.movingTiles.remove(tile)
                continue
            elif distance < 0.75:
                braking = log(distance + 10, 10) - 1
                deltaX *= braking * 30
                deltaY *= braking * 30

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
        self.z = 0

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
        glTranslatef(self.x, self.y, self.z)
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
        glOrtho(-1.0, 1.0, -1.0, 1.0, 1.0, 100.0)

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

        glScalef(*tiles.scale)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor4f(1, 1, 1, 1)

        tiles.draw()


    win.push_handlers(tiles)

    @win.event
    def on_key_release(symbol, modifiers):
        print tiles.getTileAtColumnRow(1, 0)

        if symbol == pyglet.window.key.RIGHT:
            #tiles.moveTiles(1, EAST)
            tiles.floatingTile.rotate(CLOCKWISE)
        elif symbol == pyglet.window.key.LEFT:
            #tiles.moveTiles(2, WEST)
            tiles.floatingTile.rotate(ANTICLOCKWISE)
        elif symbol == pyglet.window.key.UP:
            tiles.moveTiles(1, NORTH)
        elif symbol == pyglet.window.key.DOWN:
            tiles.moveTiles(2, SOUTH)

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

