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

class Board(object):
    def __init__(self):
        self.tileBatch = pyglet.graphics.Batch()
        self.sprites = []

        self.moving = (0, 0)

        for y in range(0, 9):
            tempRow = []
            for x in range(0, 12):
                tempRow.append(Tile(x * 81 + OFFSET_X,
                                    y * 81 + OFFSET_Y,
                                    tileType=random.randint(1, 3),
                                    tileRotation=random.randint(0, 3),
                                    batch=self.tileBatch))
            self.sprites.append(tempRow)

        self.floatingTile = Tile(-100, -100,
                                 tileType=random.randint(1, 3),
                                 tileRotation=random.randint(0, 3),
                                 batch=self.tileBatch)

        pyglet.clock.schedule(self.update)

    def moveRow(self, row, direction):
        assert direction in [board.EAST, board.WEST]
        assert self.moving == (0, 0)

        self.moving = (direction, row)

        if direction == board.EAST:
            self.floatingTile.x = self.sprites[row][0].x - 81
            self.floatingTile.y = self.sprites[row][0].y
            self.floatingTile.moveToY = self.floatingTile.y

            self.sprites[row][0:0] = [self.floatingTile]
            self.floatingTile = self.sprites[row][-1]
            self.floatingTile.moveToX = self.floatingTile.x + 81
            self.sprites[row] = self.sprites[row][:-1]

        elif direction == board.WEST:
            self.floatingTile.x = self.sprites[row][-1].x + 81
            self.floatingTile.y = self.sprites[row][-1].y
            self.floatingTile.moveToY = self.floatingTile.y

            self.sprites[row].append(self.floatingTile) 

            self.floatingTile = self.sprites[row][0]
            self.floatingTile.moveToX = self.floatingTile.x - 81
            self.sprites[row][0:1] = []

        self.floatingTile.moving = direction

        for tile in self.sprites[row]:
            if direction == board.EAST:
                tile.moveToX = tile.x + 81
            elif direction == board.WEST:
                tile.moveToX = tile.x - 81


    def moveColumn(self, column, direction):
        assert direction in [board.NORTH, board.SOUTH]
        assert not self.moving

        self.moving = True

        for row in range(9):
            tile = self.sprites[row][column]
            if direction == board.NORTH:
                tile.moveToY = tile.y + 81
            elif direction == board.SOUTH:
                tile.moveToY = tile.y - 81

    def update(self, dt):
        def resetTile(tile):
            tile.x = tile.moveToX
            tile.y = tile.moveToY

        direction, pos = self.moving

        if direction == board.EAST:
            for tile in self.sprites[pos] + [self.floatingTile]:
                if tile.x < tile.moveToX:
                    tile.x += dt * 40
                else:
                    resetTile(tile)
                    
        elif direction == board.WEST:
            for tile in self.sprites[pos] + [self.floatingTile]:
                if tile.x > tile.moveToX:
                    tile.x -= dt * 40
                else:
                    resetTile(tile)

#
#        if self.moving:
#            for row in self.sprites:
#                for tile in row:
#                    if tile.moving == board.EAST:
#                        if tile.x < tile.moveToX:
#                            tile.x += dt * 40
#                        else:
#                            tile.x = tile.moveToX
#                            tile.moving = 0
#                            self.moving = False
#                    elif tile.moving == board.WEST:
#                        if tile.x > tile.moveToX:
#                            tile.x -= dt * 40
#                        else:
#                            tile.x = tile.moveToX
#                            tile.moving = 0
#                            self.moving = False
#                    elif tile.moving == board.NORTH:
#                        if tile.y < tile.moveToY:
#                            tile.y += dt * 40
#                        else:
#                            tile.y = tile.moveToY
#                            tile.moving = 0
#                            self.moving = False
#                    elif tile.moving == board.SOUTH:
#                        if tile.y > tile.moveToY:
#                            tile.y -= dt * 40
#                        else:
#                            tile.y = tile.moveToY
#                            tile.moving = 0
#                            self.moving = False


    def draw(self):
        self.tileBatch.draw()

title = Title()
gameBoard = Board()
gameBoard.moveRow(2, board.EAST)
#gameBoard.moveColumn(2, board.NORTH)

@window.event
def on_draw():
    window.clear()
    gameBoard.draw()
    title.draw()

pyglet.app.run()

