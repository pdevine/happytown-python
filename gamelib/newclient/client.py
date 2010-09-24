
from math import sin
import pyglet
import random

from pyglet.gl import *
from pyglet import resource

window = pyglet.window.Window(1024, 650)

pyglet.font.add_file('LOKISD__.TTF')

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
            letterImg.abs_y = 500

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
        self.rotation = 0

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.rotation += 10 * dt

    def draw(self):
        glPushMatrix()
        glColor4f(0.2, 0.2, 0.2, 0.2)
        glTranslatef(500, 500, 0)
        glRotated(self.rotation, 0, 0, 1)

        pyglet.graphics.draw(12, GL_TRIANGLES,
            ('v2i', (0, 0, -100, -700, 100, -700,
                     0, 0, -100, 700, 100, 700,
                     0, 0, 700, 100, 700, -100,
                     0, 0, -700, 100, -700, -100)))
        #self.sprite.draw()

        glTranslatef(-500, -500, 0)


        glPopMatrix()


title = Title()
sun = Sun()
fps_display = pyglet.clock.ClockDisplay()

def setup():
    #glClearColor(.5, .5, .5, 1)
    pass

@window.event
def on_draw():
    window.clear()
    sun.draw()
    title.draw()
    fps_display.draw()

setup()

pyglet.app.run()


