import pyglet
from pyglet.gl import *

import tiles
from tiles import TileT, TileL, TileI
import random

class Scene(object):
    def __init__(self):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

class Board(Scene):
    tileSizes = {
        (3, 3) : tiles.BOARD_SMALL,
        (4, 4) : tiles.BOARD_MEDIUM,
        (5, 5) : tiles.BOARD_MEDIUM,
        (6, 6) : tiles.BOARD_MEDIUM,
        (7, 7) : tiles.BOARD_LARGE,
    }
    def __init__(self, rows=7, columns=7):

        self.tiles = []
        self.tokens = []
        self.people = []

        self.rows = rows
        self.columns = columns

        tileSize = self.tileSizes[(rows, columns)]

        startX = -(columns / 2 * 4)
        startY = rows / 2 * 4

        # shift the rows/columns to not be centered for even #'d columns
        if not rows % 2:
            startY -= 2

        if not columns % 2:
            startX += 2

        tileChoices = [TileT, TileL, TileI]
        yOffset = startY

        for y in range(rows):
            xOffset = startX
            for x in range(columns):
                tileType = random.choice(tileChoices)

                self.tiles.append(
                    tileType(
                        xOffset,
                        yOffset,
                        tileSize,
                        random.randint(0, 3)))
                xOffset += 4
            yOffset -= 4

        tileType = random.choice(tileChoices)
        self.floatingTile = tileType(
            -100,
            -100,
            tileSize,
            random.randint(0, 3))
            

    def draw(self):
        for tile in self.tiles:
            tile.draw()

    def setup(self):
        pass

if __name__ == '__main__':
    win = pyglet.window.Window(width=1024, height=768)
    angle = 0.0

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

    sel = 0
    b = Board()

    @win.event
    def on_draw():
        win.clear()

        glLoadIdentity()

        glPolygonMode(GL_FRONT, GL_FILL)
        glColor4f(1, 1, 1, 1)

        glRotatef(-30, 1, 0, 0)
        b.draw()

#    @win.event
#    def on_key_release(symbol, modifiers):
#        global sel
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
    
    init()

    pyglet.app.run()

