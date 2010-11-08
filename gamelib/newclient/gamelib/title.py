
from math import sin, radians
import pyglet
import random
import scene

from pyglet.gl import *
from pyglet import resource

window = pyglet.window.Window(1024, 768)

resource.path.append('../fonts/')
resource.path.append('../res/')
resource.reindex()

resource.add_font('LOKISD__.TTF')

class Title(scene.Scene):
    def __init__(self):
        offset = 50
        self.tick = 0
        self.letters = []

        self.batch = pyglet.graphics.Batch()

        colors = [
            (252, 182, 83, 255),
            (255, 82, 84, 255),
            (206, 232, 121, 255)
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

        glClearColor(92/255.0, 172/255.0, 196/255.0, 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.sun = Sun()

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.tick += dt
        for count, letter in enumerate(self.letters):
            letter.x = letter.abs_x
            letter.y = sin(self.tick * 3 + count) * 20 + letter.abs_y

    def draw(self):
        self.sun.draw()
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        print "keypress"
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        glColor4f(1, 1, 1, 1)
        window.clear()
        self.draw()
        #return pyglet.event.EVENT_HANDLED

class Sun:
    def __init__(self):
        self.x = 850
        self.y = 550
        self.img = resource.image('sun.png')
        self.img.anchor_x = self.img.width / 2
        self.img.anchor_y = self.img.height / 2
        self.rotation = 0

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.rotation += 600 * dt

    def draw(self):
        radRotation = radians(self.rotation)

        glPushMatrix()
        glColor4f(0.9, 0.9, 0.9, 0.2)
        glTranslatef(self.x, self.y, 0)
        glRotated(radRotation, 0, 0, 1)

        pyglet.graphics.draw(12, GL_TRIANGLES,
            ('v2i', (0, 0, -100, -900, 100, -900,
                     0, 0, -100, 900, 100, 900,
                     0, 0, 900, 100, 900, -100,
                     0, 0, -900, 100, -900, -100)))

        glRotated(-radRotation, 0, 0, 1)
        glRotated(-radRotation, 0, 0, 1)

        #glColor4f(0.6, 0.6, 0.6, 0.2)
        glColor4f(0.7, 0.7, 0.7, 0.2)

        pyglet.graphics.draw(12, GL_TRIANGLES,
            ('v2i', (0, 0, -100, -900, 100, -900,
                     0, 0, -100, 900, 100, 900,
                     0, 0, 900, 100, 900, -100,
                     0, 0, -900, 100, -900, -100)))


        glTranslatef(-self.x, -self.y, 0)
        glPopMatrix()

        glPushMatrix()
        glColor4f(1, 1, 1, 1)
        glTranslatef(self.x, self.y, 0)
        glRotated(sin(radRotation / 10) * 20, 0, 0, 1)
        self.img.blit(0, 0)
        glTranslatef(-self.x, -self.y, 0)
        glPopMatrix()

        glColor4f(140/255.0, 209/255.0, 157/255.0, 1)
        pyglet.graphics.draw(6, GL_TRIANGLES,
            ('v2i', (0, 0, 0, 300, 1024, 300,
                     0, 0, 1024, 300, 1024, 0)))

if __name__ == '__main__':
    title = Title()
    fps_display = pyglet.clock.ClockDisplay()

    @window.event
    def on_draw():
        fps_display.draw()

    window.push_handlers(title)

    pyglet.app.run()


