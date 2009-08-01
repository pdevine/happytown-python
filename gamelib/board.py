import random

ROWS = 7
COLUMNS = 7

TILE_I = 1
TILE_L = 2
TILE_T = 3

NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4

class Tile(object):
    # dictionary of tile type and rotations to the direction
    # players can enter/leave the tile
    tileDirections = {
        (TILE_L, 0) : (EAST, SOUTH),
        (TILE_L, 1) : (SOUTH, WEST),
        (TILE_L, 2) : (WEST, NORTH),
        (TILE_L, 3) : (NORTH, EAST),
        (TILE_I, 0) : (NORTH, SOUTH),
        (TILE_I, 1) : (EAST, WEST),
        (TILE_I, 2) : (NORTH, SOUTH),
        (TILE_I, 3) : (EAST, WEST),
        (TILE_T, 0) : (EAST, SOUTH, WEST),
        (TILE_T, 1) : (NORTH, EAST, SOUTH),
        (TILE_T, 2) : (NORTH, EAST, WEST),
        (TILE_T, 3) : (NORTH, EAST, SOUTH),
    }

    def __init__(self, tileType, tileRotation):
        self.setTypeAndRotation(tileType, tileRotation)

    def setTypeAndRotation(self, tileType, tileRotation):
        self.tileType = tileType
        self.tileRotation = tileRotation

    def hasDir(self, direction):
        directionKey = (self.tileType, self.tileRotation)
        return direction in self.tileDirections[directionKey]

class BoardMovementException(Exception):
    pass

class Board(object):
    def __init__(self, rows=ROWS, columns=COLUMNS):
        self.createBoard(rows, columns, 0)

    def createBoard(self, rows, columns, players):
        self.rows = rows
        self.columns = columns
        self.players = players
        self.board = []

        def randomTileType():
            return random.choice([TILE_I, TILE_L, TILE_T])

        for row in range(rows):
            tempRow = []
            for column in range(columns):
                tileType = randomTileType()
                tileRotation = random.randint(0, 3)
                tempRow.append(Tile(tileType, tileRotation))
            self.board.append(tempRow)

        self.board[0][0].setTypeAndRotation(TILE_L, 0)
        self.board[0][columns-1].setTypeAndRotation(TILE_L, 1)
        self.board[rows-1][0].setTypeAndRotation(TILE_L, 3)
        self.board[rows-1][columns-1].setTypeAndRotation(TILE_L, 2)

        self.floatingTile = Tile(randomTileType(), 0)

    def moveRow(self, row, direction):

        if direction not in [EAST, WEST]:
            raise BoardMovementException(
                "Tried to move board in the wrong direction")
        

        if row == 0 or row == self.rows - 1:
            raise BoardMovementException(
                "Can't move the corners")

        if direction == WEST:
            newFloatingTile = self.board[row][0]
            self.board[row][0:1] = []
            self.board[row].append(self.floatingTile)

        elif direction == EAST:
            newFloatingTile = self.board[row][self.columns-1]
            self.board[row] = self.board[row][:-1]
            self.board[row][0:0] = [self.floatingTile]

        self.floatingTile = newFloatingTile

    def moveColumn(self, column, direction):

        if direction not in [NORTH, SOUTH]:
            raise BoardMovementException(
                "Tried to move board in the wrong direction")

        if column == 0 or column == self.columns - 1:
            raise BoardMovementException(
                "Can't move the corners")

        if direction == NORTH:
            newFloatingTile = self.board[0][column]

            for row in range(self.rows-1):
                self.board[row][column] = self.board[row+1][column]

            self.board[self.rows-1][column] = self.floatingTile

        elif direction == SOUTH:
            newFloatingTile = self.board[self.rows-1][column]

            for row in range(self.rows-1, 0, -1):
                self.board[row][column] = self.board[row-1][column]

            self.board[0][column] = self.floatingTile

        self.floatingTile = newFloatingTile


    def asciiBoard(self):
        buf = ''

        for row in self.board:
            for tile in row:
                if tile.hasDir(NORTH):
                    buf = buf + "   |  "
                else:
                    buf = buf + "      "
            buf = buf + "\n"
            for tile in row:
                if tile.hasDir(WEST):
                    buf = buf + " --"
                else:
                    buf = buf + "   "

                buf = buf + "+"

                if tile.hasDir(EAST):
                    buf = buf + "--"
                else:
                    buf = buf + "  "
            buf = buf + "\n"
            for tile in row:
                if tile.hasDir(SOUTH):
                    buf = buf + "   |  "
                else:
                    buf = buf + "      "
            buf = buf + "\n"
        return buf

if __name__ == '__main__':
    b = Board()
    print b.asciiBoard()
    b.moveColumn(1, SOUTH)
    print b.asciiBoard()
    b.moveColumn(1, SOUTH)
    print b.asciiBoard()
