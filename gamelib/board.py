import random
import traverse

ROWS = 7
COLUMNS = 7

TILE_I = 1
TILE_L = 2
TILE_T = 3

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

class Tile(object):
    # dictionary of tile type and rotations to the direction
    # players can enter/leave the tile
    tileDirections = {
        (TILE_L, 0) : EAST | SOUTH,
        (TILE_L, 1) : SOUTH | WEST,
        (TILE_L, 2) : WEST | NORTH,
        (TILE_L, 3) : NORTH | EAST,
        (TILE_I, 0) : NORTH | SOUTH,
        (TILE_I, 1) : EAST | WEST,
        (TILE_I, 2) : NORTH | SOUTH,
        (TILE_I, 3) : EAST | WEST,
        (TILE_T, 0) : EAST | SOUTH | WEST,
        (TILE_T, 1) : NORTH | EAST | SOUTH,
        (TILE_T, 2) : NORTH | EAST | WEST,
        (TILE_T, 3) : NORTH | EAST | SOUTH,
    }

    def __init__(self, tileType, tileRotation, playerHome=0):
        self.setTypeAndRotation(tileType, tileRotation)
        self.playerHome = playerHome
        self.players = []

    def rotateClockwise(self):
        if self.tileRotation == 3:
            self.tileRotation = 0
        else:
            self.tileRotation += 1

    def rotateCounterClockwise(self):
        if self.tileRotation == 0:
            self.tileRotation = 3
        else:
            self.tileRotation -= 1

    def setTypeAndRotation(self, tileType, tileRotation):
        self.tileType = tileType
        self.tileRotation = tileRotation

    def hasDir(self, direction):
        directionKey = (self.tileType, self.tileRotation)
        return direction & self.tileDirections[directionKey]

    def hasPlayer(self, player):
        return player in self.players

    def asciiTile(self):
        buf = ''
        if self.hasDir(NORTH):
            buf = buf + "   |  "
        else:
            buf = buf + "      "
        buf += '\n'

        if self.hasDir(WEST):
            buf = buf + " --"
        else:
            buf = buf + "   "

        buf = buf + "+"

        if self.hasDir(EAST):
            buf = buf + "--"
        else:
            buf = buf + "  "
        buf = buf + "\n"

        if self.hasDir(SOUTH):
            buf = buf + "   |  "
        else:
            buf = buf + "      "
        buf = buf + "\n"

        return buf

class Player(object):
    def __init__(self, playerNumber):
        self.playerNumber = playerNumber

        self.name = "Player %d" % playerNumber

class BoardMovementError(Exception):
    pass

class BoardCreationError(Exception):
    pass

class PlayerMovementError(Exception):
    pass

class Board(object):
    def __init__(self, rows=ROWS, columns=COLUMNS):
        self.createBoard(rows, columns, players=2)

    def createBoard(self, rows, columns, players):
        self.rows = rows
        self.columns = columns
        self.board = []
        self.players = []

        if players < 2:
            raise BoardCreationError(
                "Must have 2 or more players to start a game")

        # players are enumerated from 1
        for player in range(1, players+1):
            self.players.append(Player(player))

        self.playerTurn = 1
        self.floatingTilePushed = False

        def randomTileType():
            return random.choice([TILE_I, TILE_L, TILE_T])

        for row in range(rows):
            tempRow = []
            for column in range(columns):
                tileType = randomTileType()
                tileRotation = random.randint(0, 3)
                tempRow.append(Tile(tileType, tileRotation))
            self.board.append(tempRow)

        setPlayerHomeTile(0, 0, TILE_L, 0, 1)
        setPlayerHomeTile(0, columns-1, TILE_L, 1, 2)
        setPlayerHomeTile(rows-1, 0, TILE_L, 3, 3)
        setPlayerHomeTile(rows-1, columns-1, TILE_L, 2, 4)

        #self.board[0][columns-1].setTypeAndRotation(TILE_L, 1)
        #self.board[0][columns-1].setTypeAndRotation(TILE_L, 1)
        #self.board[rows-1][0].setTypeAndRotation(TILE_L, 3)
        #self.board[rows-1][columns-1].setTypeAndRotation(TILE_L, 2)

        self.floatingTile = Tile(randomTileType(), 0)

    def setPlayerHomeTile(row, column, tile, rotation, player):
        self.board[row][column].setTypeAndRotation(tile, rotation)
        self.board[row][column].playerHome = player

    def getFloatingTile(self):
        return self.floatingTile

    def moveRow(self, row, direction):
        '''Shift a row on the board horizontally'''

        if self.floatingTilePushed:
            raise BoardMovementError(
                "Floating tile already pushed")

        if direction not in [EAST, WEST]:
            raise BoardMovementError(
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

        self.floatingTilePushed = True

    def moveColumn(self, column, direction):
        '''Shift a column on the board vertically'''

        if self.floatingTilePushed:
            raise BoardMovementError(
                "Floating tile already pushed")

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

        self.floatingTilePushed = True


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

    def movePlayer(self, player):
        if player != self.playerTurn:
            raise PlayerMovementError(
                "Player moved out of turn")

        traverseGraph = traverse.TraversalGraph(self)

if __name__ == '__main__':
    b = Board()
    print b.asciiBoard()
    ft = b.getFloatingTile()
    print ft.asciiTile()
    ft.rotateClockwise()
    print ft.asciiTile()

    ft.rotateClockwise()
    print ft.asciiTile()

    b.moveColumn(1, SOUTH)
    print b.asciiBoard()
    b.moveColumn(1, SOUTH)
    print b.asciiBoard()
