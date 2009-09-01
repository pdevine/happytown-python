import board
import random
import pyglet

import xmlrpclib

#window = pyglet.window.Window(1024, 768)
window = pyglet.window.Window(fullscreen=True)

pyglet.font.add_file('../data/depraved.ttf')
pyglet.font.add_file('../data/jamaistevie.ttf')

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

class Title(object):
    def __init__(self):
        self.label_front = \
            pyglet.text.Label('Truva',
                              font_name='Depraved',
                              font_size=120,
                              color=(255, 50, 0, 255),
                              x=512,
                              y=670,
                              anchor_x='center', 
                              anchor_y='center')

        self.label_back = \
            pyglet.text.Label('Truva',
                              font_name='Depraved',
                              font_size=120,
                              color=(255, 255, 255, 255),
                              x=502,
                              y=670,
                              anchor_x='center', 
                              anchor_y='center')

        pyglet.clock.schedule(self.update)

        self.timer = 2

        self.positions = (670, 665)

    def update(self, dt):
        self.timer -= dt

        if self.timer <= 0:
            if self.label_front.y == self.positions[0]:
                self.label_front.y = self.positions[1]
                self.label_back.y = self.positions[1] - 10
            else:
                self.label_front.y = self.positions[0]
                self.label_back.y = self.positions[0] - 10

            if self.timer <= -0.5:
                self.timer = random.randint(1, 5)

    def draw(self):
        self.label_back.draw()
        self.label_front.draw()

class Tile(pyglet.sprite.Sprite):
    def __init__(self, x, y, color=(255, 255, 255), tileType=1,
                       tileRotation=0, batch=None):

        pyglet.sprite.Sprite.__init__(self, TILE_IMAGES[tileType], batch=batch)

        self.x = x
        self.y = y

        self.moveToX = x
        self.moveToY = y

        self.rotation = tileRotation * 90

        self.color = color

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
    def __init__(self, demo=False):
        self.tileBatch = pyglet.graphics.Batch()
        self.sprites = []

        self.moving = (0, 0)
        self.movingTiles = []

        # make the colour dimmer if we're not running in a real game
        color = (255, 255, 255)
        if demo:
            color = (150, 150, 150)

        for y in range(ROWS):
            tempRow = []
            for x in range(COLUMNS):
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

class Menu(object):
    def __init__(self):
        self.labels = [
            pyglet.text.Label('New Game',
                              font_name='jamaistevie',
                              font_size=50,
                              x=170,
                              y=500),
            pyglet.text.Label('Join Game',
                              font_name='jamaistevie',
                              font_size=50,
                              x=170,
                              y=400),
            pyglet.text.Label('Quit',
                              font_name='jamaistevie',
                              font_size=50,
                              x=170,
                              y=300),
        ]

        self.selected = -1
        self.highlighted = -1

        self.shadow = ShadowImage()

    def mousePress(self, x, y, button, modifiers):
        self.selected = -1

        for count, label in enumerate(self.labels):
            if x > label.x and x < label.x + label.content_width and \
               y > label.y and y < label.y + label.content_height:
                label.x += 5
                label.y -= 5
                self.selected = count
                break

    def mouseRelease(self, x, y, button, modifiers):
        if self.selected > -1:
            label = self.labels[self.selected]
            label.x -= 5
            label.y += 5

    def mouseMotion(self, x, y, dx, dy):
        # turn off the highlight colour
        if self.highlighted > -1:
            label = self.labels[self.highlighted]
            label.color = (255, 255, 255, 255)

        for count, label in enumerate(self.labels):
            if x > label.x and x < label.x + label.content_width and \
               y > label.y and y < label.y + label.content_height:
                label.color = (255, 50, 50, 255)
                self.highlighted = count
                break


    def update(self, dt):
        pass

    def draw(self):
        for label in self.labels:
            label.draw()

        self.shadow.draw()

class ShadowImage(pyglet.sprite.Sprite):
    def __init__(self, imageName='../data/spartan.png'):
        img = pyglet.image.load(imageName) 
        pyglet.sprite.Sprite.__init__(self, img)

        self.opacity = 50
        self.color = (100, 100, 100)
        self.x = 700
        self.scale = 1.5

class NetworkGame(object):
    def __init__(self, serverUrl='http://localhost:8000'):
        gameServer = xmlrpclib.ServerProxy(serverUrl)

        self.serverResponding = True

        try:
            self.gameList = gameServer.listGames()
        except socket.error:
            self.serverResponding = False
            self.gameList = []


title = Title()
gameBoard = Board(demo=True)
menu = Menu()

@window.event
def on_draw():
    window.clear()
    gameBoard.draw()
    title.draw()
    menu.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    menu.mousePress(x, y, button, modifiers)

@window.event
def on_mouse_release(x, y, button, modifiers):
    menu.mouseRelease(x, y, button, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
    menu.mouseMotion(x, y, dx, dy)

pyglet.app.run()

