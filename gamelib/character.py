import pyglet
import board

from pyglet.window import key
from sprite import AnimatedSprite

class Character(AnimatedSprite):
    def __init__(self):
        img = pyglet.image.load('../data/person1.png')
        image_grid = pyglet.image.ImageGrid(img, 4, 4)

        self.walking = True
        self.direction = board.SOUTH
        self.frame_duration = 0.20

        AnimatedSprite.__init__(self,
            image_grid.get_animation(self.frame_duration))

        self.walk_south()

    def walk_north(self):
        self.play()
        self.set_loop(0, 4)

    def walk_east(self):
        self.play()
        self.set_loop(4, 8)

    def walk_west(self):
        self.play()
        self.set_loop(8, 12)

    def walk_south(self):
        self.play()
        self.set_loop(12, 16)

    def rest(self):
        self.set_frame(14)
        self.pause()

    def keyPress(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.walk_east()
        elif symbol == key.LEFT:
            self.walk_west()
        elif symbol == key.UP:
            self.walk_north()
        elif symbol == key.DOWN:
            self.walk_south()
        elif symbol == key.SPACE:
            self.rest()

