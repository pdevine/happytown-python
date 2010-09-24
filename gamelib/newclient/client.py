
from math import sin, radians
import pyglet
import random

from pyglet.gl import *
from pyglet import resource

window = pyglet.window.Window(1024, 650)

pyglet.font.add_file('fonts/LOKISD__.TTF')

class Title:
    def __init__(self):
        offset = 50
        self.tick = 0
        self.letters = []

        self.batch = pyglet.graphics.Batch()

        colors = [
            (54, 171, 138, 255),
            (63, 66, 51, 255),
            (142, 179, 21, 255),
            (202, 230, 46, 255),
            (255, 85, 0, 255)
        ]

        for letter in 'HAPPYTOWN':
            letterImg = pyglet.text.Label(
                letter,
                font_name='LoKinderSchrift',
                font_size=120,
                italic=True,
                color=random.choice(colors),
                anchor_x='left',
                anchor_y='baseline',
                batch=self.batch)
            letterImg.abs_x = offset
            letterImg.abs_y = 400

            self.letters.append(letterImg)
            offset += letterImg.content_width

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.tick += dt
        for count, letter in enumerate(self.letters):
            letter.x = letter.abs_x
            letter.y = sin(self.tick * 3 + count) * 20 + letter.abs_y

    def draw(self):
        self.batch.draw()

class Sun:
    def __init__(self):
        self.x = 850
        self.y = 550
        self.img = pyglet.image.load('sun.png')
        self.img.anchor_x = self.img.width / 2
        self.img.anchor_y = self.img.height / 2
        self.rotation = 0

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.rotation += 600 * dt

    def draw(self):
        radRotation = radians(self.rotation)

        glPushMatrix()
        glColor4f(0.7, 0.7, 0.7, 0.2)
        glTranslatef(self.x, self.y, 0)
        glRotated(radRotation, 0, 0, 1)

        pyglet.graphics.draw(12, GL_TRIANGLES,
            ('v2i', (0, 0, -100, -800, 100, -800,
                     0, 0, -100, 800, 100, 800,
                     0, 0, 800, 100, 800, -100,
                     0, 0, -800, 100, -800, -100)))
        #self.sprite.draw()

        glTranslatef(-self.x, -self.y, 0)
        glPopMatrix()

        glPushMatrix()
        glColor4f(1, 1, 1, 1)
        glTranslatef(self.x, self.y, 0)
        glRotated(sin(radRotation / 10) * 20, 0, 0, 1)
        self.img.blit(0, 0)
        glTranslatef(-self.x, -self.y, 0)
        glPopMatrix()


title = Title()
sun = Sun()
fps_display = pyglet.clock.ClockDisplay()

def setup():
    glClearColor(11/255.0, 126/255.0, 214/255.0, 1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

@window.event
def on_draw():
    window.clear()
    sun.draw()
    title.draw()
    fps_display.draw()

setup()

pyglet.app.run()


