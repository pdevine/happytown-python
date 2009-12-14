import pyglet
import random
import board

from math import sqrt, sin, cos, atan2, log

TILE_IMAGES = (
    '',
    pyglet.image.load('../../data/tile-i3.png'),
    pyglet.image.load('../../data/tile-l3.png'),
    pyglet.image.load('../../data/tile-t3.png'),
)

for img in TILE_IMAGES:
    if img:
        img.anchor_x = 41
        img.anchor_y = 41

OFFSET_X = 65
OFFSET_Y = 55

ROWS = 9
COLUMNS = 12

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
        self.moveSpeed = 100

        self.slowDown = True

        self.rotateTo = (0, 0)
        self.rotation = tileRotation * 90

        self.color = color


    def rotate(self, direction):
        if direction == CLOCKWISE:
            if self.rotation + 90 >= 360:
                self.rotation -= 360
            self.rotateTo = (self.rotation + 90, CLOCKWISE)
        else:
            if self.rotation - 90 <= 0:
                self.rotation += 360
            self.rotateTo = (self.rotation - 90, ANTICLOCKWISE)

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

    def update(self, dt):
        if self.rotateTo[1] == CLOCKWISE:
            if self.rotation < self.rotateTo[0]:
                self.rotation += self.rotationSpeed * dt
            else:
                self.rotation = self.rotateTo[0]
                self.rotateTo = (0, 0)
                pyglet.clock.unschedule(self.update)
        elif self.rotateTo[1] == ANTICLOCKWISE:
            if self.rotation > self.rotateTo[0]:
                self.rotation -= self.rotationSpeed * dt
            else:
                self.rotation = self.rotateTo[0]
                self.rotateTo = (0, 0)
                pyglet.clock.unschedule(self.update)

class AnimateBoard(object):
    def slideIn(self):
        self.moving = True
        print "start moving"
        count = 0
        for tile in self.sprites:
            tile.x = 1024 + tile.x
            tile.moveSpeed = 700
            self.movingTiles.append(tile)

    def pourIn(self):
        self.moving = True
        for tile in self.sprites:
            tile.y = 768 + tile.y + (self.rows - tile.row) * 60
            tile.moveSpeed = 700
            self.movingTiles.append(tile)

class Board(AnimateBoard):
    def __init__(self, columns=COLUMNS, rows=ROWS, demo=False,
                 fadeColor=(100, 100, 100)):
        self.tileBatch = pyglet.graphics.Batch()
        self.sprites = []

        self.moving = False
        self.movingTiles = []

        self.columns = columns
        self.rows = rows

        # make the colour dimmer if we're not running in a real game
        self.demo = demo
        self.color = (255, 255, 255)
        self.fadeColor = fadeColor

        for y in range(rows):
            for x in range(columns):
                self.sprites.append(Tile(x * 81 + OFFSET_X,
                                         768 - (y * 81) - OFFSET_Y,
                                         x, y,
                                         color=self.color,
                                         tileType=random.randint(1, 3),
                                         tileRotation=random.randint(0, 3),
                                         batch=self.tileBatch))

        self.floatingTile = Tile(-100, -100, -1, -1,
                                 color=self.color,
                                 tileType=random.randint(1, 3),
                                 tileRotation=random.randint(0, 3),
                                 batch=self.tileBatch)

        pyglet.clock.schedule(self.update)

    def rotateTiles(self, direction=CLOCKWISE):
        for tile in self.sprites:
            pyglet.clock.schedule(tile.update)
            tile.rotate(direction)

    def moveTiles(self, pos, direction):
        assert direction in [board.NORTH, board.EAST, board.SOUTH, board.WEST]
        assert self.moving == False

        #self.moving = (direction, pos)

        self.moving = True
        self.movingTiles = []

        if direction in [board.EAST, board.WEST]:
            for tile in self.sprites:
                if tile.row != pos:
                    continue
                self.movingTiles.append(tile)

            self.movingTiles.sort(lambda x, y: cmp(x.column, y.column))

            if direction == board.EAST:
                tile = self.movingTiles[0]
                self.floatingTile.x = tile.x - 81
                self.floatingTile.y = tile.y
                self.floatingTile.moveToY = tile.y
                self.floatingTile.moveToX = tile.x
                self.floatingTile.row = pos
                self.floatingTile.column = -1

                self.movingTiles.insert(0, self.floatingTile)
                self.sprites.append(self.floatingTile)

                self.floatingTile = self.movingTiles[-1]
                self.sprites.remove(self.floatingTile)

                for tile in self.movingTiles:
                    tile.moveToX = tile.x + 81
                    tile.column += 1
                    tile.moveSpeed = 100


            elif direction == board.WEST:
                tile = self.movingTiles[-1]
                self.floatingTile.x = tile.x + 81
                self.floatingTile.y = tile.y
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y
                self.floatingTile.row = pos
                self.floatingTile.column = self.columns

                self.movingTiles.append(self.floatingTile)
                self.sprites.append(self.floatingTile)

                self.floatingTile = self.movingTiles[0]
                self.sprites.remove(self.floatingTile)

                for tile in self.movingTiles:
                    tile.moveToX = tile.x - 81
                    tile.column -= 1
                    tile.moveSpeed = 100


        elif direction in [board.NORTH, board.SOUTH]:
            for tile in self.sprites:
                if tile.column != pos:
                    continue
                self.movingTiles.append(tile)

            self.movingTiles.sort(lambda x, y: cmp(x.row, y.row))

            if direction == board.NORTH:
                tile = self.movingTiles[-1]
                self.floatingTile.x = tile.x
                self.floatingTile.y = tile.y - 81
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y
                self.floatingTile.column = pos
                self.floatingTile.row = self.rows

                self.movingTiles.append(self.floatingTile)
                self.sprites.append(self.floatingTile)

                self.floatingTile = self.movingTiles[0]
                self.sprites.remove(self.floatingTile)

                for tile in self.movingTiles:
                    tile.moveToY = tile.y + 81
                    tile.row -= 1
                    tile.moveSpeed = 100

            elif direction == board.SOUTH:
                tile = self.movingTiles[0]
                self.floatingTile.x = tile.x
                self.floatingTile.y = tile.y + 81
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y
                self.floatingTile.column = pos
                self.floatingTile.row = -1

                self.movingTiles.insert(0, self.floatingTile)
                self.sprites.append(self.floatingTile)

                self.floatingTile = self.movingTiles[-1]
                self.sprites.remove(self.floatingTile)

                for tile in self.movingTiles:
                    tile.moveToY = tile.y - 81
                    tile.row += 1
                    tile.moveSpeed = 100


    def update(self, dt):
        if not self.movingTiles and self.color != self.fadeColor:
            colors = []
            for count, val in enumerate(self.color):
                if val > self.fadeColor[count]:
                    colors.append(
                        max(self.fadeColor[count], int(val - 10 * dt)))
                else:
                    colors.append(self.fadeColor[count])
            self.color = tuple(colors)

            for tile in self.sprites:
                tile.color = self.color

            self.floatingTile.color = self.color

        if self.moving:
            for tile in self.movingTiles:
                opp = tile.moveToX - tile.x
                adj = tile.moveToY - tile.y

                rad = atan2(opp, adj)

                tile.velocityX = tile.moveSpeed * dt * sin(rad)
                tile.velocityY = tile.moveSpeed * dt * cos(rad)

                #tile.velocityX = tile.moveSpeed * dt * sin(tile.rotation)
                #tile.velocityY = tile.moveSpeed * dt * cos(tile.rotation)

                distance = sqrt(pow(tile.moveToX - tile.x, 2) + \
                                pow(tile.moveToY - tile.y, 2))

                if distance < 1:
                    tile.reset()
                    self.movingTiles.remove(tile)
                    continue
                elif distance < 100:
                    braking = log(distance+10, 10) - 1
                    tile.velocityX *= braking
                    tile.velocityY *= braking

                tile.x += tile.velocityX
                tile.y += tile.velocityY

        if self.demo and not self.movingTiles and self.color == self.fadeColor:
            self.moving = False
            direction = random.choice([board.NORTH,
                                       board.EAST,
                                       board.SOUTH,
                                       board.WEST])
            if direction in [board.NORTH, board.SOUTH]:
                self.moveTiles(random.randint(0, self.columns-1), direction)
            else:
                self.moveTiles(random.randint(0, self.rows-1), direction)

    def draw(self):
        self.tileBatch.draw()

if __name__ == '__main__':
    from pyglet.window import key

    window = pyglet.window.Window(1024, 768)

    b = Board(7, 7)
    b.pourIn()

    #pyglet.clock.unschedule(b.update)

    #pyglet.clock.schedule(b.update)

    @window.event
    def on_draw():
        window.clear()
        b.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        pass

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        pass

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol == key.RIGHT:
            b.rotateTiles(CLOCKWISE)
            print "right"
        elif symbol == key.LEFT:
            b.rotateTiles(ANTICLOCKWISE)
            print "left"
        elif symbol == key.SPACE:
            b.demo = not b.demo

    @window.event
    def on_key_press(symbol, modifiers):
        pass

    pyglet.app.run()

