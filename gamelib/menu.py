import sys
import colorsys
import pyglet
from pyglet.window import key

FACES = pyglet.image.load('../data/faces.png')

class Menu(object):
    def __init__(self, labels=None, labelColor=(255, 255, 255, 255),
                       highlightColor=(255, 50, 50, 255)):
        self.labels = []
        if labels:
            self.labels = self.labels

        self.labelColor = labelColor
        self.highlightColor = highlightColor

        self.selected = -1
        self.highlighted = -1
        self.execute = False

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

            for count, label in enumerate(self.labels):
                if x > label.x and x < label.x + label.content_width and \
                   y > label.y and y < label.y + label.content_height:
                    if self.selected == count:
                        self.execute = True
                        break

    def mouseMotion(self, x, y, dx, dy):
        self._removeHighlight()

        for count, label in enumerate(self.labels):
            if x > label.x and x < label.x + label.content_width and \
               y > label.y and y < label.y + label.content_height:
                self._setHighlight(label)
                self.highlighted = count
                break

    def keyPress(self, symbol, modifiers):
        if symbol == key.ENTER:
            pass
        elif symbol == key.UP:
            self._removeHighlight()

            self.highlighted -= 1
            if self.highlighted <= -1:
                self.highlighted = len(self.labels)-1

            self._setHighlight(self.labels[self.highlighted])

        elif symbol == key.DOWN:
            self._removeHighlight()

            self.highlighted += 1
            if self.highlighted >= len(self.labels):
                self.highlighted = 0

            self._setHighlight(self.labels[self.highlighted])

    def keyRelease(self, symbol, modifiers):
        pass

    def _setHighlight(self, label):
        label.color = self.highlightColor

    def _removeHighlight(self):
        if self.highlighted > -1:
            label = self.labels[self.highlighted]
            label.color = self.labelColor

        for label in self.labels:
            label.draw()

    def draw(self):
        for label in self.labels:
            label.draw()

class MainMenu(Menu):
    def __init__(self):
        Menu.__init__(self)

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

        self.shadow = ShadowImage()

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        if self.execute:
            if self.selected == 0:
                pass
            if self.selected == 2:
                sys.exit(0)

    def draw(self):
        Menu.draw(self)
        self.shadow.draw()

class PlayerImage(pyglet.sprite.Sprite):
    def __init__(self, image, x, y):
        pyglet.sprite.Sprite.__init__(self, image, x, y)

    def draw(self):
        pyglet.sprite.Sprite.draw(self)

class Selector(object):
    def __init__(self, hue=0.23, x=0, y=0):
        assert hue >= 0.0 and hue <= 1.0
        self.hsv = [hue, 0, 1]
        self.increasing = True

        self.x = x
        self.y = y

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        saturation = self.hsv[1]
        if self.increasing:
            saturation += dt * 1.25
        else:
            saturation -= dt * 1.25

        if saturation > 1.0:
            self.increasing = False
            saturation = 1.0
        elif saturation < 0.0:
            self.increasing = True
            saturation = 0.0

        self.hsv[1] = saturation

    def draw(self):
        pyglet.gl.glLineWidth(4)
        r, g, b = colorsys.hsv_to_rgb(*self.hsv)
        pyglet.gl.glColor4f(r, g, b, 1.0)
        pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
            ('v2i',
                (self.x, self.y,
                 self.x+100, self.y,
                 self.x+100, self.y+100,
                 self.x, self.y+100)))

class NewGameMenu(object):
    def __init__(self):
        self.playerImages = []
        image_grid = pyglet.image.ImageGrid(FACES, 2, 4)

        count = 0
        for row in range(4):
            for col in range(2):
                self.playerImages.append(PlayerImage(image_grid[count],
                                         row * 150 + 150, col * 100 + 200))
                count += 1

        self.selected = 0
        self.selector = Selector()

        self.selector.x = self.playerImages[self.selected].x
        self.selector.y = self.playerImages[self.selected].y

    def mousePress(self, *args):
        pass

    def mouseRelease(self, *args):
        pass

    def mouseMotion(self, *args):
        pass

    def keyPress(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.selected += 1
            self.selector.x = self.playerImages[self.selected].x
            self.selector.y = self.playerImages[self.selected].y
        elif symbol == key.LEFT:
            self.selected -= 1
            self.selector.x = self.playerImages[self.selected].x
            self.selector.y = self.playerImages[self.selected].y

    def keyRelease(self, *args):
        pass

    def draw(self):
        for player in self.playerImages:
            player.draw()

        self.selector.draw()


class ShadowImage(pyglet.sprite.Sprite):
    def __init__(self, imageName='../data/spartan.png'):
        img = pyglet.image.load(imageName)
        pyglet.sprite.Sprite.__init__(self, img)

        self.opacity = 50
        self.color = (100, 100, 100)
        self.x = 700
        self.scale = 1.5


