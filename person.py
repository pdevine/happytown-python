import util
import pygame
import board
import tile
import animation

from options import *
from pygame.locals import *

class Person(animation.Animation):

    def __init__(self, player=PLAYER1, file="person1.png", items=[1, 2, 3],
                 size=(32,48), location=(0,0), board=None, computer=True,
                 name="Computer1"):

        pygame.sprite.Sprite.__init__(self)
        self.walkCycle = [[], [], [], [], []]
        self.walk_path = []

        image = util.loadImage(file)
        for x in range(4):
            print x* size[0]
            print x*size[1]
            self.walkCycle[SOUTH].append(image.subsurface(
                pygame.Rect(x*size[0], 0*size[1], size[0], size[1])))
            self.walkCycle[WEST].append(image.subsurface(
                pygame.Rect(x*size[0], 1*size[1], size[0], size[1])))
            self.walkCycle[EAST].append(image.subsurface(
                pygame.Rect(x*size[0], 2*size[1], size[0], size[1])))
            self.walkCycle[NORTH].append(image.subsurface(
                pygame.Rect(x*size[0], 3*size[1], size[0], size[1])))

        self.items = items
        self.home = location
        self.name = name

        self.location = location
        self.dir = SOUTH
        self.frame = 0

        self.image = self.walkCycle[self.dir][self.frame]
        self.imageCopy = self.walkCycle[self.dir][self.frame]

        self.warping = False
        self.moving = False
        self.sliding = -1
        self.boardStatus = None

        tile = board.getTile(location)

        self.rect = self.image.get_rect()
        self.rect.center = tile.getTileLocation().center
        self.lastLocation = None

        self.board = board

        self.tick = 0

    def moveToTile(self, board, traversal, endPoint):
        self.walk_path = []
        for location in traversal.findPath(self.location, endPoint):
            self.walk_path.append(board.getTile(location))

        nextColumn = self.walk_path[1].column
        nextRow = self.walk_path[1].row

        self.dir = findDir(self.location, (nextColumn, nextRow))

        self.walk_path = self.walk_path[1:]
        self.moving = True

        self.boardStatus = board.floating_tile

    def update(self):
        self.tick += 1

        # never let a person start walking around until after the
        # floating tile has stopped sliding.

        if self.boardStatus and self.boardStatus.sliding > -1 and \
           not self.sliding > -1:
            return

        if self.sliding > -1:
            self.slide()
        elif self.falling:
            self.fall()
        elif self.tick % 4 == 0 and self.moving:
            self.frame += 1

            if self.frame >= 4:
                self.frame = 0

        if self.walk_path:
            (x1, y1) = self.rect.center
            (x2, y2) = self.walk_path[0].rect.center

            if self.dir == SOUTH and y2 > y1:
                self.rect.bottom += 3
            elif self.dir == NORTH and y2 < y1:
                self.rect.top -= 3
            elif self.dir == EAST and x2 > x1:
                self.rect.right += 3
            elif self.dir == WEST and x2 < x1:
                self.rect.left -= 3
            else:
                self.location = (self.walk_path[0].column,
                    self.walk_path[0].row)
                self.lastLocation = self.walk_path[0]
                self.walk_path = self.walk_path[1:]
                if self.walk_path:
                    nextLocation = (self.walk_path[0].column,
                        self.walk_path[0].row)
                    self.dir = findDir(self.location, nextLocation)
                else:
                    if self.lastLocation and self.lastLocation.item:
                        if self.lastLocation.item.offset in self.items:
                            # pick up the item
                            self.items.remove(self.lastLocation.item.offset)
                            self.board.item_sprites.remove(self.lastLocation.item)
            self.image = self.walkCycle[self.dir][self.frame]
        else:
            self.moving = False


def findDir(location1, location2):
    (col1, row1) = location1
    (col2, row2) = location2

    if col2 > col1:
        return EAST
    if col2 < col1:
        return WEST
    if row2 > row1:
        return SOUTH
    if row2 < row1:
        return NORTH

    return -1

if __name__ == "__main__":
    Person()
