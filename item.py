import util
import pygame
import board
import animation

from options import *
from pygame.locals import *

class Item(animation.Animation):
    image = None

    def __init__(self, file="items.png", size=(50,50), location=(0,0),
        offset=0):

        pygame.sprite.Sprite.__init__(self)

        rect = pygame.Rect(offset*size[0], 0, size[0], size[1])
        if Item.image is None:
            Item.image = util.loadImage(file)

        self.image = Item.image.subsurface(rect)
        self.imageCopy = self.image
        self.location = location

        self.offset = offset

        self.rect = self.image.get_rect()
        self.rect.center = board.findPosition(location)

        self.falling = False
        self.sliding = -1
        self.tick = 0

