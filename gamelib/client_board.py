import pyglet
import random
import board

from math import sqrt, sin, cos, atan2, log

TILE_IMAGES = (
    '',
    pyglet.image.load('../data/tile-i3.png'),
    pyglet.image.load('../data/tile-l3.png'),
    pyglet.image.load('../data/tile-t3.png'),
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
    def __init__(self, x, y, color=(255, 255, 255), tileType=1,
                       tileRotation=0, batch=None):

        pyglet.sprite.Sprite.__init__(self, TILE_IMAGES[tileType], batch=batch)

        self.rotationSpeed = 120

        self.x = x
        self.y = y

        self.velocityX = 0
        self.velocityY = 0

        self.moveToX = x
        self.moveToY = y

        self.slowDown = True

        self.rotateTo = (0, 0)
        #self.rotation = tileRotation * 90

        self.color = color

        pyglet.clock.schedule(self.update)

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
        elif self.rotateTo[1] == ANTICLOCKWISE:
            if self.rotation > self.rotateTo[0]:
                self.rotation -= self.rotationSpeed * dt
            else:
                self.rotation = self.rotateTo[0]
                self.rotateTo = (0, 0)

class AnimateBoard(object):
    def slideIn(self):
        self.moving = True
        print "start moving"
        count = 0
        for row in self.sprites:
            for tile in row:
                tile.finalPos = tile.x
                tile.x = 1024 + tile.x + (count * 81)
                tile.moveDirection = board.WEST
                tile.moveSpeed = 400
                self.movingTiles.append(tile)
            count += 1



class Board(AnimateBoard):
    def __init__(self, columns=COLUMNS, rows=ROWS, demo=False):
        self.tileBatch = pyglet.graphics.Batch()
        self.sprites = []

        self.moving = False
        self.movingTiles = []

        # make the colour dimmer if we're not running in a real game
        color = (255, 255, 255)
        if demo:
            color = (150, 150, 150)

        for y in range(rows):
            tempRow = []
            for x in range(columns):
                tempRow.append(Tile(x * 81 + OFFSET_X,
                                    768 - (y * 81) - OFFSET_Y,
                                    color=color,
                                    tileType=random.randint(1, 3),
                                    tileRotation=random.randint(0, 3),
                                    batch=self.tileBatch))
            self.sprites.append(tempRow)

        self.floatingTile = Tile(-100, -100,
                                 color=color,
                                 tileType=random.randint(1, 3),
                                 tileRotation=random.randint(0, 3),
                                 batch=self.tileBatch)

        pyglet.clock.schedule(self.update)

    def rotateTiles(self, direction=CLOCKWISE):
        for row in self.sprites:
            for tile in row:
                tile.rotate(direction)

    def moveTiles(self, pos, direction):
        assert direction in [board.NORTH, board.EAST, board.SOUTH, board.WEST]
        assert self.moving == False

        #self.moving = (direction, pos)

        self.moving = True
        self.movingTiles = []

        if direction == board.EAST:
            self.floatingTile.x = self.sprites[pos][0].x - 81
            self.floatingTile.y = self.sprites[pos][0].y
            self.floatingTile.moveToY = self.sprites[pos][0].y
            self.floatingTile.moveDirection = direction
            self.sprites[pos].insert(0, self.floatingTile)

            for tile in self.sprites[pos]:
                tile.moveToX = tile.x + 81
                tile.moveDirection = direction
                self.movingTiles.append(tile)

            self.floatingTile = self.sprites[pos][-1]
            self.sprites[pos] = self.sprites[pos][:-1]

        elif direction == board.WEST:
            self.floatingTile.x = self.sprites[pos][-1].x + 81
            self.floatingTile.y = self.sprites[pos][-1].y
            self.floatingTile.moveToY = self.sprites[pos][-1].y
            self.floatingTile.moveDirection = direction
            self.sprites[pos].append(self.floatingTile)

            for tile in self.sprites[pos]:
                tile.moveToX = tile.x - 81
                tile.moveDirection = direction
                self.movingTiles.append(tile)

            self.floatingTile = self.sprites[pos][0]
            self.sprites[pos][0:1] = []

        elif direction == board.NORTH:
            rows = len(self.sprites)
            self.floatingTile.x = self.sprites[rows-1][pos].x
            self.floatingTile.y = self.sprites[rows-1][pos].y - 81
            self.floatingTile.moveToX = self.sprites[rows-1][pos].x
            self.floatingTile.moveToY = self.sprites[rows-1][pos].y
            self.floatingTile.moveDirection = direction

            newFloatingTile = self.sprites[0][pos]

            for row in range(rows):
                tile = self.sprites[row][pos]
                tile.moveToY = tile.y + 81
                tile.moveDirection = direction
                self.movingTiles.append(tile)
                if row < rows-1:
                    self.sprites[row][pos] = self.sprites[row+1][pos]
                else:
                    self.sprites[row][pos] = self.floatingTile

            self.movingTiles.append(self.floatingTile)
            self.floatingTile = newFloatingTile

        elif direction == board.SOUTH:
            rows = len(self.sprites)
            self.floatingTile.x = self.sprites[0][pos].x
            self.floatingTile.y = self.sprites[0][pos].y + 81
            self.floatingTile.moveToX = self.sprites[0][pos].x
            self.floatingTile.moveToY = self.sprites[0][pos].y
            self.floatingTile.moveDirection = direction

            newFloatingTile = self.sprites[rows-1][pos]

            for row in range(rows)[::-1]:
                tile = self.sprites[row][pos]
                tile.moveToY = tile.y - 81
                tile.moveDirection = direction
                self.movingTiles.append(tile)
                if row > 0:
                    self.sprites[row][pos] = self.sprites[row-1][pos]
                else:
                    self.sprites[row][pos] = self.floatingTile

            self.movingTiles.append(self.floatingTile)
            self.floatingTile = newFloatingTile

    def update(self, dt):
        if self.moving:
            for tile in self.movingTiles:
                opp = tile.moveToX - tile.x
                adj = tile.moveToY - tile.y

                rad = atan2(opp, adj)

                tile.velocityX = 8 * sin(rad)
                tile.velocityY = 15 * cos(rad)

                distance = sqrt(pow(tile.moveToX - tile.x, 2) + \
                                pow(tile.moveToY - tile.y, 2))

                if distance < 10:
                    tile.x = tile.moveToX
                    tile.y = tile.moveToY
                    tile.reset()
                    self.movingTiles.remove(tile)
                    continue
                elif distance < 100:
                    braking = log(distance, 10) - 1
                    tile.velocityX *= braking
                    tile.velocityY *= braking

                tile.x += tile.velocityX
                tile.y += tile.velocityY

        #if not self.movingTiles:
        #    self.moving = False
        #    direction = random.choice([board.NORTH,
        #                               board.EAST,
        #                               board.SOUTH,
        #                               board.WEST])
        #    if direction in [board.NORTH, board.SOUTH]:
        #        self.moveTiles(random.randint(0, COLUMNS-1), direction)
        #    else:
        #        self.moveTiles(random.randint(0, ROWS-1), direction)

    def draw(self):
        self.tileBatch.draw()

if __name__ == '__main__':
    from pyglet.window import key

    window = pyglet.window.Window(1024, 768)

    b = Board(7, 7)
    b.slideIn()

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

    @window.event
    def on_key_press(symbol, modifiers):
        pass

    pyglet.app.run()

