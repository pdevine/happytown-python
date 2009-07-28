import pygame
#from board import findPosition
import board
from options import *

class Animation(pygame.sprite.Sprite):
    image = None
    rect = None

    sliding = False
    falling = False
    location = None

    tick = 0

    def fallen(self):
        (column, row) = self.location
        if column == 0:
            self.location = (COLUMNS-1, row)
        elif column == COLUMNS-1:
            self.location = (0, row)
        elif row == 0:
            self.location = (column, ROWS-1)
        elif row == ROWS-1:
            self.location = (column, 0)
        self.rect = self.image.get_rect()
        self.rect.center = board.findPosition(self.location)

    def fall(self):
        center = self.rect.center
        width = self.image.get_width()
        height = self.image.get_height()

        try:
            self.image = pygame.transform.scale(self.image,
                (width-5, height-5))
            self.rect = self.image.get_rect(center=center)
        except ValueError:
            self.falling = False
            self.image = self.imageCopy

            self.fallen()


    def slide(self, direction=-1, location=None, rect=None, speed=3):
        if not location:
            location = self.location
        if not rect:
            rect = self.rect

        (column, row) = location
        position = rect.center

        if direction == -1:
            direction = self.sliding

        if direction == EAST:
            destination = board.findPosition((column+1, row))
            if position[COLUMN] >= destination[COLUMN]:
                self.sliding = -1
                if column+1 == COLUMNS:
                    self.falling = True
                else:
                    self.location = (column+1, row)
            else:
                rect.left += speed
        elif direction == WEST:
            destination = board.findPosition((column-1, row))
            if position[COLUMN] <= destination[COLUMN]:
                self.sliding = -1
                if column-1 == -1:
                    self.falling = True
                else:
                    self.location = (column-1, row)
            else:
                rect.left -= speed
        elif direction == NORTH:
            destination = board.findPosition((column, row-1))
            if position[ROW] <= destination[ROW]:
                self.sliding = -1
                if row-1 == -1:
                    self.falling = True
                else:
                    self.location = (column, row-1)
            else:
                rect.top -= speed
        elif direction == SOUTH:
            destination = board.findPosition((column, row+1))
            if position[ROW] >= destination[ROW]:
                self.sliding = -1
                if row+1 == ROWS:
                    self.falling = True
                else:
                    self.location = (column, row+1)
            else:
                rect.top += 3

    def bounce(self, speed=2):
        if not self.movement:
            if self.direction == SOUTH:
                self.rect.top += speed
            elif self.direction == NORTH:
                self.rect.top -= speed
            elif self.direction == EAST:
                self.rect.left += speed
            elif self.direction == WEST:
                self.rect.left -= speed
        else:
            if self.direction == SOUTH:
                self.rect.top -= speed
            elif self.direction == NORTH:
                self.rect.top += speed
            elif self.direction == EAST:
                self.rect.left -= speed
            elif self.direction == WEST:
                self.rect.left += speed


    def update(self):
        self.tick += 1

        if self.sliding > -1:
            self.slide()
        elif self.falling:
            self.fall()

    

