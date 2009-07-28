import pygame

from pygame.locals import *
from options import *

import arrow
import tile
import util
import board
import traverse
import person
import ai

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.done = False

        self.bg = pygame.Surface(screen.get_size())
        self.bg = self.bg.convert()
        self.bg.fill((52, 56, 91))

        self.arrows = []
        self.arrow_sprites = pygame.sprite.Group()
        for x in range(1, 6):
            self.arrows.append(arrow.Arrow(NORTH, (x, 7)))
            self.arrows.append(arrow.Arrow(EAST, (-1, x)))
            self.arrows.append(arrow.Arrow(SOUTH, (x, -1)))
            self.arrows.append(arrow.Arrow(WEST, (7, x)))

        self.tile_sprites = pygame.sprite.Group()
        self.board = board.Board()
        self.board.item_sprites = pygame.sprite.Group()

        for row in self.board.getBoard():
            for tile in row:
                self.tile_sprites.add(tile)
                if tile.item:
                    self.board.item_sprites.add(tile.item)

        self.floating_tile_sprite = pygame.sprite.Group()
        self.floating_tile_sprite.add(self.board.getFloatingTile())

        self.turn = PLAYER1

        #self.people = []
        #self.people.append(person.Person(board=self.board))
        #self.people.append(person.Person(board=self.board, file="person2.png",
        #                       location=(6, 6)))

        self.people_sprites = pygame.sprite.Group()

        for character in self.board.people:
            self.people_sprites.add(character)

        self.totalPlayers = len(self.board.people)

        self.board.printBoard()

    def run(self):
        while not self.done:
            tiles = self.board

            for arrow in self.arrows:
                arrow.update()

            for row in self.board.board:
                for tile in row:
                    tile.update()
                    if tile.item:
                        tile.item.update()

            floatingTile = self.board.getFloatingTile()
            floatingTile.update()
            if floatingTile.item:
                floatingTile.item.update()

            for person in self.board.people:
                person.update()


            self.draw()
            self.handleEvents()

    def draw(self):
        # blit + sprite draw stuff here
        self.screen.blit(self.bg, self.screen.get_rect())
        self.arrow_sprites.draw(self.screen)
        self.tile_sprites.draw(self.screen)

        # update the tiles before objects/people if we're not stuck to the
        # mouse
        if not self.board.floating_tile.trackMouse:
            self.floating_tile_sprite.draw(self.screen)
        self.board.item_sprites.draw(self.screen)
        self.people_sprites.draw(self.screen)

        if self.board.floating_tile.trackMouse:
            self.floating_tile_sprite.draw(self.screen)

        pygame.display.flip()

    def handleEvents(self):
        pygame.event.post(pygame.event.wait())
        for event in pygame.event.get():
            if event.type == QUIT:
                self.done = True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    #ai.Computer(self.board, self, self.turn).findMove()
                    print self.board.people[self.turn].items
                elif event.key == K_RIGHT:
                    self.board.floating_tile.rotate(CLOCKWISE)
                elif event.key == K_LEFT:
                    self.board.floating_tile.rotate(COUNTERCLOCKWISE)
                elif event.key == K_ESCAPE:
                    self.done = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == 4:
                    self.board.floating_tile.rotate(CLOCKWISE)
                elif event.button == 5:
                    self.board.floating_tile.rotate(COUNTERCLOCKWISE)
                elif event.button == 1:
                    if self.board.floating_tile.sliding > -1 or \
                       self.board.floating_tile.falling:
                        continue

                    (column, row) = board.findLocation(event.pos)
                    #tiles = self.board.board
                    tile = self.board.getTile((column, row))

                    if not tile:
                        self.addFloatingTileToBoard()

                        if column == -1:
                            if self.board.moveRow(row, EAST):
                                self.removeArrows()
                        elif column == self.board.getTotalColumns():
                            if self.board.moveRow(row, WEST):
                                self.removeArrows()
                        elif row == -1:
                            if self.board.moveColumn(column, SOUTH):
                                self.removeArrows()
                        elif row == self.board.getTotalRows():
                            if self.board.moveColumn(column, NORTH):
                                self.removeArrows()

                        self.removeFloatingTileFromBoard()

                    elif tile:
                        startPoint = self.board.people[self.turn].location
                        endPoint = (tile.column, tile.row)
                        if startPoint != endPoint:
                            t = traverse.TraversalGraph(self.board)
                            if t.findPath(startPoint, endPoint):
                                self.board.people[self.turn].moveToTile(
                                    self.board, t, endPoint)
                                self.turn += 1
                                if self.turn >= self.totalPlayers:
                                    self.turn = PLAYER1

                    else:
                        if self.board.floating_tile.trackMouse:
                            self.board.floating_tile.trackMouse = False
                            self.removeArrows()
                        else:
                            self.board.floating_tile.trackMouse = True
                            self.addArrows()
                            lastMove = self.board.getLastMove()
                            if lastMove:
                                self.removeArrowAtLocation(
                                    findArrowLocation(lastMove))
                       # self.board.floating_tile.trackMouse = True

    def addFloatingTileToBoard(self):
        self.floating_tile_sprite.remove(self.board.floating_tile)
        self.tile_sprites.add(self.board.floating_tile)

    def removeFloatingTileFromBoard(self):
        self.tile_sprites.remove(self.board.floating_tile)
        self.floating_tile_sprite.add(self.board.floating_tile)

    def addArrows(self):
        for arrow in self.arrows:
            self.arrow_sprites.add(arrow)

    def removeArrows(self):
        for arrow in self.arrows:
            self.arrow_sprites.remove(arrow)

    def removeArrowAtLocation(self, location):
        for arrow in self.arrows:
            if arrow.getLocation() == location:
                self.arrow_sprites.remove(arrow)

def findArrowLocation(lastMove):
    (position, direction) = lastMove
    if direction == NORTH:
        return (position, -1)
    elif direction == EAST:
        return (COLUMNS, position)
    elif direction == SOUTH:
        return (position, ROWS)
    elif direction == WEST:
        return (-1, position)
    return None

