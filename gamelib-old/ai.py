import board
import traverse
import copy
from options import *

class Computer:

    def __init__(self, board, game, player, items):
        self.savedBoard = board
        self.game = game
        self.items = board.people[player].items
        self.player = player
        self.itemLocation = []
        self.board = None
        self.lastRotation = 0

    def resetBoard(self):
        '''
           Undo the last move or completely reset the board if we haven't
           started shifting the board yet
        '''
        if self.board and self.board.lastMove:
            (place, direction) = self.board.lastMove
            if direction == NORTH:
                self.board.moveColumn(place, SOUTH)
            elif direction == SOUTH:
                self.board.moveColumn(place, NORTH)
            elif direction == EAST:
                self.board.moveRow(place, WEST)
            elif direction == WEST:
                self.board.moveRow(place, EAST)
            self.board.floating_tile = copy.deepcopy(self.savedTile)
        else:
            self.board = copy.deepcopy(self.savedBoard)
            self.savedTile = self.board.floating_tile

        #self.board = copy.deepcopy(self.savedBoard)
        self.itemLocation = []

    def findMove(self):
        self.resetBoard()
        startPoint = self.board.people[self.player].location

        columns = []
        rows = []
        rotation = []

        # starting with column 1 or row 1 is kind of silly --
        # we should start at where the player is, and then spread out from
        # there

        columns = [1, 2, 3, 4, 5]
        rows = [1, 2, 3, 4, 5]

        if self.board.floating_tile.type == TILE_I:
            rotation = [0, 1]
        else:
            rotation = [0, 1, 2, 3]

        # this should be cleaned up a little

        for column in columns:
            if not self.savedBoard.lastMove == (column, NORTH):
                for turn in rotation:
                    self.board.floating_tile.rotateTile(turns=turn)
                    self.board.moveColumn(column, SOUTH)
                    startPoint = self.board.people[self.player].location
                    if self.findItems(startPoint):
                        self.moveColumnOrRow(startPoint, turn, COLUMN, column, SOUTH)
                        return True
                    self.resetBoard()

            if not self.savedBoard.lastMove == (column, SOUTH):
                for turn in rotation:
                    self.board.floating_tile.rotateTile(turns=turn)    
                    self.board.moveColumn(column, NORTH)
                    startPoint = self.board.people[self.player].location
                    if self.findItems(startPoint):
                        self.moveColumnOrRow(startPoint, turn, COLUMN, column, NORTH)
                        return True
                    self.resetBoard()

        for row in rows:
            if not self.savedBoard.lastMove == (row, WEST):
                for turn in rotation:
                    self.board.floating_tile.rotateTile(turns=turn)
                    self.board.moveRow(row, EAST)
                    startPoint = self.board.people[self.player].location
                    if self.findItems(startPoint):
                        self.moveColumnOrRow(startPoint, turn, ROW, row, EAST)
                        return True
                    self.resetBoard()

            if not self.savedBoard.lastMove == (row, EAST):
                for turn in rotation:
                    self.board.floating_tile.rotateTile(turns=turn)
                    self.board.moveRow(row, WEST)
                    startPoint = self.board.people[self.player].location
                    if self.findItems(startPoint):
                        self.moveColumnOrRow(startPoint, turn, ROW, row, WEST)
                        return True
                    self.resetBoard()

        # what do we do if we didn't find any moves?


    def moveColumnOrRow(self, startPoint, floatingTileTurns, type,
        place, direction):

        self.savedBoard.floating_tile.rotateTile(turns=floatingTileTurns)

        self.game.addFloatingTileToBoard()
        if type == COLUMN:
            self.savedBoard.moveColumn(place, direction)
        elif type == ROW:
            self.savedBoard.moveRow(place, direction)
        self.game.removeFloatingTileFromBoard()

        t = traverse.TraversalGraph(self.board)
        itemLocation = self.findItems(startPoint)

        self.savedBoard.people[self.player].moveToTile(self.savedBoard, t, itemLocation)
        

    def findItems(self, startPoint):
        '''Return the location of a found item'''
        self.findItemLocations()
        t = traverse.TraversalGraph(self.board)
        for location in self.itemLocation:
            if t.findPath(startPoint, location):
                return location

    def findItemLocations(self):
        '''Find the location of each item needed by the person'''
        for row in range(self.board.getTotalRows()):
            for column in range(self.board.getTotalColumns()):
                tile = self.board.board[row][column]
                if tile.item and tile.item.offset in self.items:
                    self.itemLocation.append((column, row))


