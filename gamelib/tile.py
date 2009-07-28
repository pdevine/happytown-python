import pygame
import util
import board
import animation

from options import *
from pygame.locals import *

class Tile(animation.Animation):
    image = None

    _bit_lookup = {
        "0-0": 5,
        "0-1": 10,
        "0-2": 5,
        "0-3": 10,
        "1-0": 3, 
        "1-1": 6,
        "1-2": 12,
        "1-3": 9,
        "2-0": 14,
        "2-1": 13,
        "2-2": 11,
        "2-3": 7
    }

    def __init__(self, type=TILE_T, rotation=0, column=-1, row=-1,
                 item=None, people=0, home=-1, resting=False):

        pygame.sprite.Sprite.__init__(self)
        self.set_orientation(type, rotation)
        self.item = item
        self.people = people
        self.home = home

        self.location = (column, row)

        self.column = column
        self.row = row

        if not self.image:
            if type == TILE_I:
                image = util.loadImage("tile-i3.png")
            elif type == TILE_T:
                image = util.loadImage("tile-t3.png")
            elif type == TILE_L:
                image = util.loadImage("tile-l3.png")

            if rotation:
                image = pygame.transform.rotate(image, -90 * rotation)


        self.width = image.get_width()
        self.height = image.get_height()
        self.type = type

        self.rect = self.getTileLocation()

        self.sliding = -1
        self.rotating = -1
        self.rotation = 0
        self.rotated = 0
        self.image = image
        self.imageCopy = image
        self.falling = False
        self.trackMouse = False
        self.tick = 0

        # put the floating tile in the correct location
        if resting:
            self.fallen()
        else:
            self.resting = False

# XXX - this is code for if you want to tie a given object to a tile,
#       which is kind of dorky since the images look super weird when rotated
#
#    def setItem(self, itemNumber):
#        print itemNumber
#        image = util.loadImage("objects.png")
#        objectImage = image.subsurface(pygame.Rect(itemNumber*50, 0, 50, 50))
#        self.image.blit(objectImage, (16, 10))
#        pass

    def setTile(self, location=None, sliding=None, realign=False):
        if location:
            self.location = location
        if sliding > -1:
            self.sliding = sliding
            if self.item:
                self.item.sliding = sliding
        if realign:
            self.rect = self.getTileLocation()

    def has_dir(self, dir):
        if self._bit_lookup[self.orientation] >> dir & 1:
            return True
        else:
            return False

#    def has_person(self, person):
#        if self.people >> person & 1:
#            return True
#        else:
#            return False
#
#    def add_person(self, person):
#        self.people = self.people | (1 << person)
#
#    def remove_person(self, person):
#       self.people = self.people ^ (1 << person)

    def rotateTile(self, turns=1, direction=CLOCKWISE):
        print "direction = %d" % direction
        for count in range(turns):
            self.rotate(direction)

    def rotate(self, direction=CLOCKWISE):
        self.rotating = direction

        (type, rotation) = self.orientation.split('-')

        rotation = int(rotation)

        if direction == CLOCKWISE:
            if rotation == 3:
                rotation = 0
            else:
                rotation = rotation + 1
            self.rotation -= 90
        else:
            if rotation == 0:
                rotation = 3
            else:
                rotation = rotation - 1
            self.rotation += 90

        self.set_orientation(type, rotation)

    def set_orientation(self, type, rotation):
        self.orientation = "%s-%d" % (type, rotation)

    def getTileLocation(self):
        width = self.width
        height = self.height
        #return pygame.Rect(self.column * (width - 1) + TILE_X_OFFSET,
        #    self.row * (height - 1) + TILE_Y_OFFSET, width, height)
        return pygame.Rect(self.location[COLUMN]* (width - 1) + TILE_X_OFFSET,
            self.location[ROW] * (height - 1) + TILE_Y_OFFSET, width, height)

    def fallen(self):
        self.resting = True
        self.location = (-1, -1)
        self.rect = self.image.get_rect()
        self.rect.center = (860, 120)

    def update(self):
        self.tick += 1

        if self.falling:
            self.fall()
        elif self.sliding > -1:
            self.slide()
        elif self.rotating == CLOCKWISE or self.rotating == COUNTERCLOCKWISE:
            if self.tick % 2 == 0:
                if self.trackMouse:
                    center = pygame.mouse.get_pos()
                else:
                    center = self.rect.center
                self.image = self.imageCopy

                if self.rotation < self.rotated:
                    self.rotated -= 15
                elif self.rotation > self.rotated:
                    self.rotated += 15
            
                self.image = pygame.transform.rotate(self.image, self.rotated)

                if self.rotated == self.rotation:
                    self.imageCopy = self.image
                    self.rotating = -1
                    self.rotation = 0
                    self.rotated = 0

                self.rect = self.image.get_rect(center=center)


        elif self.trackMouse:
            self.rect.center = pygame.mouse.get_pos()
        elif not self.resting:
            self.rect = self.getTileLocation()
        

def setItemOnTile(tile1, tile2):
    if tile1.item:
        tile2.item = tile1.item
        tile1.item = None

