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

        #self.rotation = 0
        self.rotation = tileRotation * 90

class Board(object):
    def __init__(self):
        self.tiles = pyglet.graphics.Batch()
        self.sprites = []

        for x in range(0, 12):
            for y in range(0, 9):
                self.sprites.append(Tile(x * 81 + OFFSET_X,
                                         y * 81 + OFFSET_Y,
                                         tileType=random.randint(1, 3),
                                         tileRotation=random.randint(0, 3),
                                         batch=self.tiles))

    def draw(self):
        self.tiles.draw()

title = Title()
board = Board()

@window.event
def on_draw():
    window.clear()
    board.draw()
    title.draw()

pyglet.app.run()

