import random

ROW = 1
COLUMN = 0

ROWS = 7
COLUMNS = 7

TILE_I = 1
TILE_L = 2
TILE_T = 3

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

PLAYER_1 = 1
PLAYER_2 = 2
PLAYER_3 = 4
PLAYER_4 = 8

PLAYER_BIT_VALUES = (
    0,
    PLAYER_1,
    PLAYER_2,
    PLAYER_3,
    PLAYER_4
)

import traverse
import string

class BoardMovementError(Exception):
    pass

class BoardCreationError(Exception):
    pass

class PlayerTurnError(Exception):
    pass

class PlayerMovementError(Exception):
    pass

class PlayerLocationError(Exception):
    pass

class GameOverError(Exception):
    pass

class Tile(object):
    # dictionary of tile type and rotations to the direction
    # players can enter/leave the tile
    tileToDirections = {
        (TILE_L, 0) : EAST | SOUTH,
        (TILE_L, 1) : SOUTH | WEST,
        (TILE_L, 2) : WEST | NORTH,
        (TILE_L, 3) : NORTH | EAST,
        (TILE_I, 0) : NORTH | SOUTH,
        (TILE_I, 1) : EAST | WEST,
        (TILE_I, 2) : NORTH | SOUTH,
        (TILE_I, 3) : EAST | WEST,
        (TILE_T, 0) : EAST | SOUTH | WEST,
        (TILE_T, 1) : NORTH | WEST | SOUTH,
        (TILE_T, 2) : NORTH | EAST | WEST,
        (TILE_T, 3) : NORTH | EAST | SOUTH,
    }

    # reverse of tileToDirections
    directionsToTile = dict(zip(tileToDirections.values(),
                                tileToDirections.keys()))

    def __init__(self, tileType, tileRotation, boardItem=None, playerHome=0):
        self.setTypeAndRotation(tileType, tileRotation)
        self.players = 0

        self.boardItem = boardItem
        self.playerHome = playerHome

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
        return direction & self.tileToDirections[directionKey]

    def getDirs(self):
        directions = 0
        for direction in [NORTH, EAST, SOUTH, WEST]:
            directions += self.hasDir(direction)
        return directions

    def hasPlayer(self, player):
        return PLAYER_BIT_VALUES[player] & self.players

    def addPlayer(self, player):
        assert not self.hasPlayer(player)
        self.players = PLAYER_BIT_VALUES[player] ^ self.players

    def removePlayer(self, player):
        assert self.hasPlayer(player)
        self.players = PLAYER_BIT_VALUES[player] ^ self.players

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
    def __init__(self, board, playerNumber):
        self.playerNumber = playerNumber
        self.board = board

        self.createPlayer()

    def createPlayer(self):
        self.name = "Player %d" % self.playerNumber
        self.boardItems = []

    def getAsciiItemsRemaining(self):
        return ' '.join([string.ascii_letters[item.itemNumber]
                            for item in self.boardItems
                            if not item.found]) 

    def getLocation(self):
        location = None

        for rowCount, row in enumerate(self.board.board):
            for columnCount, tile in enumerate(row):
                if tile.hasPlayer(self.playerNumber):
                    location = (columnCount, rowCount)
                    break

        if not location:
            raise PlayerLocationError("Player not found on board.")

        return location

    def setLocation(self, location):
        assert len(location) == 2

        column, row = self.getLocation()
        tile = self.board.board[row][column]
        tile.removePlayer(self.playerNumber)

        print "col=%d row=%d" % (location[COLUMN], location[ROW])
        tile = self.board.board[location[ROW]][location[COLUMN]]
        tile.addPlayer(self.playerNumber)

    location = property(getLocation, setLocation)

    def getRow(self):
        return self.getLocation()[ROW]

    row = property(getRow, None)

    def getColumn(self):
        return self.getLocation()[COLUMN]

    column = property(getColumn, None)

class BoardItem(object):
    def __init__(self, itemNumber=0):
        self.itemNumber = itemNumber
        self.found = False

class Board(object):

    def createBoard(self, players, rows=ROWS, columns=COLUMNS,
                    itemsPerPlayer=3):
        if players < 2:
            raise BoardCreationError(
                "Must have 2 or more players to start a game")

        self.gameOver = False

        self.rows = rows
        self.columns = columns
        self.board = []
        self.players = []

        # players are enumerated from 1
        for player in range(1, players+1):
            playerObj = Player(self, player)
            playerObj.createPlayer()
            self.players.append(playerObj)

        # choose a person to start
        self.playerTurn = random.randint(1, players)
        self.floatingTilePushed = False

        def randomTileType():
            return random.choice([TILE_I, TILE_L, TILE_T])

        # build up a table of random tile pieces
        for row in range(rows):
            tempRow = []
            for column in range(columns):
                tileType = randomTileType()
                tileRotation = random.randint(0, 3)
                tempRow.append(Tile(tileType, tileRotation))
            self.board.append(tempRow)

        # set up the 4 corners of the board
        self.setPlayerHomeTile(0, 0, TILE_L, 0, 1)
        self.setPlayerHomeTile(columns-1, rows-1, TILE_L, 2, 2)
        self.setPlayerHomeTile(columns-1, 0, TILE_L, 1, 3)
        self.setPlayerHomeTile(0, rows-1, TILE_L, 3, 4)

        # XXX - this should be determined by game type

        for itemNumber in range(0, itemsPerPlayer*players):
            tile = self._findFreeTileForItem()
            tile.boardItem = BoardItem(itemNumber)

            playerNumber = itemNumber / itemsPerPlayer
            self.players[playerNumber].boardItems.append(tile.boardItem)

        self.floatingTile = Tile(randomTileType(), 0)

    def _findFreeTileForItem(self):
        '''Find a free tile off the edges of the board'''
        while True:
            row = random.randint(1, self.rows-2)
            column = random.randint(1, self.columns-2)

            if not self.board[row][column].boardItem:
                return self.board[row][column]

    def setPlayerHomeTile(self, column, row, tile, rotation, player):
        self.board[row][column].setTypeAndRotation(tile, rotation)
        self.board[row][column].playerHome = player

        # set the start location for each player
        if player <= len(self.players):
            self.board[row][column].addPlayer(player)
            print "added player"

    def getFloatingTile(self):
        return self.floatingTile

    def moveRow(self, player, row, direction):
        '''Shift a row on the board horizontally'''

        if self.gameOver:
            raise GameOverError("The game is over")

        if player != self.playerTurn:
            raise BoardMovementError(
                "Player tried to move a row out of turn")

        if self.floatingTilePushed:
            raise BoardMovementError(
                "Floating tile already pushed")

        if row < 0 or row >= self.rows:
            raise BoardMovementError(
                "Row number is invalid")

        if direction not in [EAST, WEST]:
            raise BoardMovementError(
                "Tried to move board in the wrong direction")

        if row == 0 or row == self.rows - 1:
            raise BoardMovementError(
                "Can't move the corners")

        if direction == WEST:
            self.floatingTile.players = self.board[row][0].players
            self.floatingTile.boardItem = self.board[row][0].boardItem
            newFloatingTile = self.board[row][0]
            newFloatingTile.players = 0
            newFloatingTile.boardItem = None
            self.board[row][0:1] = []
            self.board[row].append(self.floatingTile)

        elif direction == EAST:
            self.floatingTile.players = self.board[row][self.columns-1].players
            self.floatingTile.boardItem = \
                self.board[row][self.columns-1].boardItem
            newFloatingTile = self.board[row][self.columns-1]
            newFloatingTile.players = 0
            newFloatingTile.boardItem = None
            self.board[row] = self.board[row][:-1]
            self.board[row][0:0] = [self.floatingTile]

        self.floatingTile = newFloatingTile

        self.floatingTilePushed = True

    def moveColumn(self, player, column, direction):
        '''Shift a column on the board vertically'''

        if self.gameOver:
            raise GameOverError("The game is over")

        if player != self.playerTurn:
            raise BoardMovementError(
                "Player tried to move a column out of turn")

        if self.floatingTilePushed:
            raise BoardMovementError(
                "Floating tile already pushed")

        if direction not in [NORTH, SOUTH]:
            raise BoardMovementError(
                "Tried to move board in the wrong direction")

        if column == 0 or column == self.columns - 1:
            raise BoardMovementError(
                "Can't move the corners")

        if direction == NORTH:
            self.floatingTile.players = self.board[0][column].players
            self.floatingTile.boardItem = self.board[0][column].boardItem
            newFloatingTile = self.board[0][column]
            newFloatingTile.players = 0
            newFloatingTile.boardItem = None

            for row in range(self.rows-1):
                self.board[row][column] = self.board[row+1][column]

            self.board[self.rows-1][column] = self.floatingTile

        elif direction == SOUTH:
            self.floatingTile.players = self.board[self.rows-1][column].players
            self.floatingTile.boardItem = \
                self.board[self.rows-1][column].boardItem
            newFloatingTile = self.board[self.rows-1][column]
            newFloatingTile.players = 0
            newFloatingTile.boardItem = None

            for row in range(self.rows-1, 0, -1):
                self.board[row][column] = self.board[row-1][column]

            self.board[0][column] = self.floatingTile

        self.floatingTile = newFloatingTile

        self.floatingTilePushed = True

    def endTurn(self, player):
        if self.gameOver:
            raise GameOverError("The game is over")

        if player != self.playerTurn:
            raise PlayerTurnError(
                "Player tried to end turn out of turn")

        # test to see if the player won
        col, row = self.players[player-1].location

        if self.board[row][col].playerHome == player and \
           self.checkIfPlayerWon(player):
            self.gameOver = True
            return

        # pick up an item if the player is on top of it
        boardItem = self.board[row][col].boardItem

        if boardItem and boardItem in self.players[player-1].boardItems:
            boardItem.found = True
            self.board[row][col].boardItem = None

        if player >= len(self.players):
            self.playerTurn = 1
        else:
            self.playerTurn += 1

        self.floatingTilePushed = False

    def checkIfPlayerWon(self, player):
        playerWon = True
        for boardItem in self.players[player-1].boardItems:
            if boardItem.found == False:
                playerWon = False
                break

        return playerWon


    def serialize(self):
        '''encode the board for quick transmission
        '''

        # TODO:  Things to serialize:
        #           - board size (row and columns)
        #           - items remaining to pick up per player
        #           - player turn
        #           - floating tile pushed
        #           - the floating tile

        buf = ''
        for row in self.board:
            for tile in row:
                buf += hex(tile.getDirs())[-1]
                buf += hex(tile.players)[-1]
                if tile.boardItem:
                    buf += string.ascii_letters[tile.boardItem.itemNumber]
                else:
                    buf += '0'
        return buf

    def deserialize(self, boardBuffer):
        count = 0

        # XXX - this should probably instantiate a new board object
        #       and pick up the board size from the serialized string

        for row in self.board:
            for tile in row:
                #assert self.board[row][tile]
                tileDirs = int(boardBuffer[count], 16)
                tile.setTypeAndRotation(*Tile.directionsToTile[tileDirs])
                tile.players = int(boardBuffer[count+1], 16)
                count += 3

    def asciiBoard(self):
        buf = ''

        def playerString(tile, playerNumber):
            if tile.hasPlayer(playerNumber):
                return str(playerNumber)
            return ' '

        for row in self.board:
            for tile in row:
                if tile.hasDir(NORTH):
                    buf = buf + "  %s|%s " % (playerString(tile, 1),
                                              playerString(tile, 2))
                else:
                    buf = buf + "  %s %s " % (playerString(tile, 1),
                                              playerString(tile, 2))
            buf = buf + "\n"
            for tile in row:
                if tile.hasDir(WEST):
                    buf = buf + " --"
                else:
                    buf = buf + "   "

                if tile.boardItem:
                    buf += string.ascii_letters[tile.boardItem.itemNumber]
                else:
                    buf += "+"

                if tile.hasDir(EAST):
                    buf = buf + "--"
                else:
                    buf = buf + "  "
            buf = buf + "\n"
            for tile in row:
                if tile.hasDir(SOUTH):
                    buf = buf + "  %s|%s " % (playerString(tile, 3),
                                              playerString(tile, 4))
                else:
                    buf = buf + "  %s %s " % (playerString(tile, 3),
                                              playerString(tile, 4))
            buf = buf + "\n"
        return buf

    def movePlayer(self, player, column, row):
        if self.gameOver:
            raise GameOverError("The game is over")

        if player != self.playerTurn:
            raise PlayerMovementError(
                "Player moved out of turn")

        if not self.floatingTilePushed:
            raise PlayerMovementError(
                "Player tried moving before pushing the floating tile")

        print "col=%d row=%d" % (column, row)

        traverseGraph = traverse.TraversalGraph(self)

        startLocation = self.players[player-1].location

        if traverseGraph.findPath(startLocation, (column, row)):
            self.players[player-1].location = (column, row)
            print "loc: col: %d row: %d" % (column, row)
        else:
            raise PlayerMovementError(
                "Can't move player from %s to (%d, %d)" % \
                    (str(startLocation), column, row))

if __name__ == '__main__':
    b = Board()
    print b.asciiBoard()
    ft = b.getFloatingTile()
    print ft.asciiTile()
    ft.rotateClockwise()
    print ft.asciiTile()

    ft.rotateClockwise()
    print ft.asciiTile()

    b.moveColumn(1, 1, SOUTH)
    print b.asciiBoard()

    b.movePlayer(1, 0, 1)
    print b.asciiBoard()

    b.endTurn(1)

    b.moveColumn(2, 1, SOUTH)
    print b.asciiBoard()

    x = b.serialize()
    print x
    #b.deserialize(x)

    #print b.asciiBoard()
