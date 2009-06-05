import pygame
import util
import board
import animation
from options import *

class Arrow(animation.Animation):
    def __init__(self, rotation, location):

        pygame.sprite.Sprite.__init__(self)
        self.image = util.loadImage("arrow.png")
        if rotation:
            self.image = pygame.transform.rotate(self.image, -90 * rotation)
        self.rect = self.image.get_rect()
        self.rect.center = (location[0] * 81 + TILE_X_OFFSET + 40,
            location[1] * 80 + TILE_Y_OFFSET + 40)

        self.tick = 0
        self.movement = 0
        self.direction = rotation
        self.location = location

    def update(self):
        self.tick += 1

        if self.tick % 2:
            self.bounce()

#            if not self.movement:
#                if self.direction == SOUTH:
#                    self.rect.top += 2
#                elif self.direction == NORTH:
#                    self.rect.top -= 2
#                elif self.direction == EAST:
#                    self.rect.left += 2
#                elif self.direction == WEST:
#                    self.rect.left -= 2
#            else:
#                if self.direction == SOUTH:
#                    self.rect.top -= 2
#                elif self.direction == NORTH:
#                    self.rect.top += 2
#                elif self.direction == EAST:
#                    self.rect.left -= 2
#                elif self.direction == WEST:
#                    self.rect.left += 2
        if self.tick % 8:
            if not self.movement:
                self.movement = 1
            else:
                self.movement = 0

    def getLocation(self):
        return self.location
