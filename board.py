import tile
import random
import string
import person
import item

from options import *

class Board:
    def __init__(self):
        self.lastMove = (None, None)
        self.createBoard()

    def createBoard(self, totalRows=ROWS, totalColumns=COLUMNS):
        board = []
        tile_i = 0
        tile_l = 0
        tile_t = 0

        for row in range(totalRows):
            boardTiles = []
            for column in range(totalColumns):
                type = tile.TILE_L
                if row == 0 and column == 0:
                    rotation = 1
                elif row == 0 and column == totalColumns-1:
                    rotation = 2
                elif row == totalRows-1 and column == totalColumns-1:
                    rotation = 3
                elif row == totalRows-1 and column == 0:
                    rotation = 0
                else:
                    type = random.randint(0, 2)
                    rotation = random.randint(0, 3)

                boardTiles.append(tile.Tile(type=type, rotation=rotation,
                    column=column, row=row))
            board.append(boardTiles)

        self.floating_tile = tile.Tile(type=random.randint(0, 2), 
            rotation=0, column=-1, row=-1, resting=True)

        board[0][0].add_person(PLAYER1)
        self.board = board

        self.sliding = 0

        self.people = []
        self.people.append(person.Person(board=self, items=[1, 2, 3]))
        self.people.append(person.Person(board=self, file="person2.png",
                               location=(6, 6), items=[4, 5, 6]))


        board[0][0].home = PLAYER1
        board[0][COLUMNS-1].home = PLAYER2
        board[ROWS-1][0].home = PLAYER3
        board[ROWS-1][COLUMNS-1].home = PLAYER4

        mObjects = range(M_OBJECTS)
        mObj = mObjects.pop()

        while mObjects:
            row = random.randint(0, ROWS-1)
            column = random.randint(0, COLUMNS-1)
            if not board[row][column].item and board[row][column].home == -1:
                board[row][column].item = item.Item(offset=mObj,
                    location=(column, row))
                mObj = mObjects.pop()

    def moveRow(self, row, direction):
        # don't move the corners
        if row == 0 or row == self.getTotalRows()-1:
            return False

        self.floating_tile.trackMouse = False

        if direction == WEST:
            self.animateRow(self.people, row, direction)

            newFloatingTile = self.board[row][0]
            newFloatingTile.setTile(sliding=WEST)

            self.board[row][0:1] = []

            newTile = self.floating_tile
            tile.setItemOnTile(newFloatingTile, newTile)
            newTile.setTile(location=(self.getTotalColumns(), row),
                            sliding=WEST, realign=True)

            self.board[row].append(newTile)

        elif direction == EAST:
            self.animateRow(self.people, row, direction)

            newFloatingTile = self.board[row][self.getTotalColumns()-1]
            newFloatingTile.setTile(sliding=EAST)
 
            self.board[row] = self.board[row][:-1]

            newTile = self.floating_tile
            tile.setItemOnTile(newFloatingTile, newTile)
            newTile.setTile(location=(-1, row), sliding=EAST, realign=True)

            self.board[row][0:0] = [newTile]

        else:
            return False

        self.floating_tile = newFloatingTile
        self.lastMove = (row, direction)
        self.updateBoard()
        return True

    def moveColumn(self, column, direction):
        # this function should probably be replaced once numpy is more
        # prevalent .. or not.

        # don't move the corners
        if column == 0 or column == self.getTotalColumns()-1:
            return False

        self.floating_tile.trackMouse = False

        if direction == NORTH:
            newFloatingTile = self.board[0][column]
            newFloatingTile.setTile(sliding=NORTH)

            for row in range(self.getTotalRows()-1):
                self.board[row][column] = self.board[row+1][column]

            self.animateColumn(self.people, column, NORTH)

            newTile = self.floating_tile
            tile.setItemOnTile(newFloatingTile, newTile)
            newTile.setTile(location=(column, self.getTotalRows()),
                sliding=NORTH, realign=True)

            self.board[self.getTotalRows()-1][column] = newTile

        elif direction == SOUTH:
            newFloatingTile = self.board[self.getTotalRows()-1][column]
            newFloatingTile.setTile(sliding=SOUTH)

            # yay for having to make a new copy in mem
            for row in range(1, self.getTotalRows())[::-1]:
                self.board[row][column] = self.board[row-1][column]

            self.animateColumn(self.people, column, SOUTH)

            newTile = self.floating_tile
            tile.setItemOnTile(newFloatingTile, newTile)
            newTile.setTile(location=(column, -1), sliding=SOUTH, realign=1)

            self.board[0][column] = newTile

        else:
            return False

        self.floating_tile = newFloatingTile
        self.lastMove = (column, direction)
        self.updateBoard()
        return True

    def getFloatingTile(self):
        return self.floating_tile

    def getBoard(self):
        return self.board

    def updateBoard(self):
        for row in range(self.getTotalRows()):
            for column in range(self.getTotalColumns()):
                self.board[row][column].column = column
                self.board[row][column].row = row

    def getTileSize(self):
        tile = self.getTile((0,0))
        return (tile.image.get_width(), tile.image.get_height())

    def getTile(self, location):
        (column, row) = location
        if row > -1 and row < self.getTotalRows() and \
           column > -1 and column < self.getTotalColumns():
            return self.board[location[ROW]][location[COLUMN]]
        return None

    def getTileAtLocation(self, location):
        return self.getTile(findLocation(location))

    def getLastMove(self):
        return self.lastMove

    def printBoard(self, tiles=None):
        if not tiles:
            tiles = self.board
        buf = ""

        items = list(string.ascii_uppercase)

        for row in tiles:
            for tile in row:
                if tile.has_dir(NORTH):
                    if tile.people:
                        buf = buf + "  %s|  " % (string.hexdigits[tile.people])
                    else:
                        buf = buf + "   |  "
                else:
                    if tile.people:
                        buf = buf + "  %s   " % (string.hexdigits[tile.people])
                    else:
                        buf = buf + "      "
            buf = buf + "\n"
            for tile in row:
                if tile.has_dir(WEST):
                    buf = buf + " --"
                else:
                    buf = buf + "   "

                if tile.item:
                    buf = buf + items[tile.item.offset-1]
                else:
                    buf = buf + "+"

                if tile.has_dir(EAST):
                    buf = buf + "--"
                else:
                    buf = buf + "  "
            buf = buf + "\n"
            for tile in row:
                if tile.has_dir(SOUTH):
                    buf = buf + "   |  "
                else:
                    buf = buf + "      "
            buf = buf + "\n"
        print buf

    def animateRow(self, people, row, direction):
        for person in people:
            if person.location[1] == row:
                person.sliding = direction

        for tile in self.board[row]:
            tile.sliding = direction
            if tile.item:
                tile.item.sliding = direction

    def animateColumn(self, people, column, direction):
        for person in people:
            if person.location[0] == column:
                person.sliding = direction

        for row in range(self.getTotalRows()):
            tile = self.board[row][column]
            tile.sliding = direction
            if tile.item:
                tile.item.sliding = direction

    def getTotalRows(self):
        return len(self.board)

    def getTotalColumns(self):
        return len(self.board[0])

def findLocation(location, width=82, height=82):
    (x, y) = location

    column = (x - TILE_X_OFFSET) / width
    row = (y - TILE_Y_OFFSET) / height

    return (column, row)

def findPosition(location, width=82, height=82):
    return (location[0] * (width - 1) + TILE_X_OFFSET + width / 2,
        location[1] * (height - 1) + TILE_Y_OFFSET + height / 2)

if __name__ == "__main__":
    Board()
