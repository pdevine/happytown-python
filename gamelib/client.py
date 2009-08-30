import board
import random
import pyglet

#window = pyglet.window.Window(1024, 768)
window = pyglet.window.Window(fullscreen=True)

pyglet.font.add_file('../data/depraved.ttf')

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

class Title(pyglet.text.Label):
    def __init__(self):
        pyglet.text.Label.__init__(self,
            'Truva',
            font_name='Depraved',
            font_size=120)
        self.color = (0, 0, 0, 255)

        pyglet.clock.schedule(self.update)

        self.x = 100
        self.y = 600
        self.timer = 2

        self.positions = (600, 595)

    def update(self, dt):
        self.timer -= dt

        if self.timer <= 0:
            if self.y == self.positions[0]:
                self.y = self.positions[1]
            else:
                self.y = self.positions[0]

            if self.timer <= -0.5:
                self.timer = random.randint(1, 5)

class Tile(pyglet.sprite.Sprite):
    def __init__(self, x, y, tileType=1, tileRotation=0, batch=None):

        pyglet.sprite.Sprite.__init__(self, TILE_IMAGES[tileType], batch=batch)

        self.x = x
        self.y = y

        self.moveToX = x
        self.moveToY = y

        self.rotation = tileRotation * 90

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

class Board(object):
    def __init__(self):
        self.tileBatch = pyglet.graphics.Batch()
        self.sprites = []

        self.moving = (0, 0)
        self.movingTiles = []

        for y in range(ROWS):
            tempRow = []
            for x in range(COLUMNS):
                tempRow.append(Tile(x * 81 + OFFSET_X,
                                    768 - (y * 81) - OFFSET_Y,
                                    tileType=random.randint(1, 3),
                                    tileRotation=random.randint(0, 3),
                                    batch=self.tileBatch))
            self.sprites.append(tempRow)

        self.floatingTile = Tile(-100, -100,
                                 tileType=random.randint(1, 3),
                                 tileRotation=random.randint(0, 3),
                                 batch=self.tileBatch)

        pyglet.clock.schedule(self.update)

    def moveTiles(self, pos, direction):
        assert direction in [board.NORTH, board.EAST, board.SOUTH, board.WEST]
        assert self.moving == (0, 0)

        self.moving = (direction, pos)

        self.movingTiles = []

        if direction == board.EAST:
            self.floatingTile.x = self.sprites[pos][0].x - 81
            self.floatingTile.y = self.sprites[pos][0].y
            self.floatingTile.moveToY = self.sprites[pos][0].y
            self.sprites[pos].insert(0, self.floatingTile)

            for tile in self.sprites[pos]:
                tile.moveToX = tile.x + 81
                self.movingTiles.append(tile)

            self.floatingTile = self.sprites[pos][-1]
            self.sprites[pos] = self.sprites[pos][:-1]

        elif direction == board.WEST:
            self.floatingTile.x = self.sprites[pos][-1].x + 81
            self.floatingTile.y = self.sprites[pos][-1].y
            self.floatingTile.moveToY = self.sprites[pos][-1].y
            self.sprites[pos].append(self.floatingTile)

            for tile in self.sprites[pos]:
                tile.moveToX = tile.x - 81
                self.movingTiles.append(tile)

            self.floatingTile = self.sprites[pos][0]
            self.sprites[pos][0:1] = []

        elif direction == board.NORTH:
            rows = len(self.sprites)
            self.floatingTile.x = self.sprites[rows-1][pos].x
            self.floatingTile.y = self.sprites[rows-1][pos].y - 81
            self.floatingTile.moveToX = self.sprites[rows-1][pos].x
            self.floatingTile.moveToY = self.sprites[rows-1][pos].y

            newFloatingTile = self.sprites[0][pos]

            for row in range(rows):
                tile = self.sprites[row][pos]
                tile.moveToY = tile.y + 81
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

            newFloatingTile = self.sprites[rows-1][pos]

            for row in range(rows)[::-1]:
                tile = self.sprites[row][pos]
                tile.moveToY = tile.y - 81
                self.movingTiles.append(tile)
                if row > 0:
                    self.sprites[row][pos] = self.sprites[row-1][pos]
                else:
                    self.sprites[row][pos] = self.floatingTile

            self.movingTiles.append(self.floatingTile)
            self.floatingTile = newFloatingTile

    def update(self, dt):
        direction, pos = self.moving

        if direction > 0:

            for tile in self.movingTiles:
                if direction == board.EAST:
                    if tile.x < tile.moveToX:
                        tile.x += dt * 40
                    else:
                        tile.reset()
                        self.movingTiles.remove(tile)
                elif direction == board.WEST:
                    if tile.x > tile.moveToX:
                        tile.x -= dt * 40
                    else:
                        tile.reset()
                        self.movingTiles.remove(tile)
                elif direction == board.NORTH:
                    if tile.y < tile.moveToY:
                        tile.y += dt * 40
                    else:
                        tile.reset()
                        self.movingTiles.remove(tile)
                elif direction == board.SOUTH:
                    if tile.y > tile.moveToY:
                        tile.y -= dt * 40
                    else:
                        tile.reset()
                        self.movingTiles.remove(tile)

        if not self.movingTiles:
            self.moving = (0, 0)
            direction = random.choice([board.NORTH,
                                       board.EAST,
                                       board.SOUTH,
                                       board.WEST])
            if direction in [board.NORTH, board.SOUTH]:
                self.moveTiles(random.randint(0, COLUMNS-1), direction)
            else:
                self.moveTiles(random.randint(0, ROWS-1), direction)

    def draw(self):
        self.tileBatch.draw()

title = Title()
gameBoard = Board()

@window.event
def on_draw():
    window.clear()
    gameBoard.draw()
    title.draw()

pyglet.app.run()

