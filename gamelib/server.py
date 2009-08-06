import time
import md5
import random
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import board
import traverse

GAME_BOARDS = {}

# 60 secs * 30 min
REMOVAL_TIME = 60 * 30

class NetworkGame(object):
    def __init__(self):
        self.board = board.Board()

        self.players = [None, None, None, None]

        self.accessTime = time.time()

    def getPlayerCount(self):
        count = 0

        for player in self.players:
            if player:
                count += 1

        return count

    playerCount = property(getPlayerCount, None)

    def getPlayer(self, playerKey):
        for player in self.players:
            if player.playerKey == playerKey:
                return player
        return None

class NetworkPlayer(object):
    def __init__(self):
        self.playerKey = createUniqueKey()
        self.accessTime = time.time()


def newGame():
    global GAME_BOARDS

    cleanupGames()

    # get a unique key for the game and set up the board
    while True:
        gameKey = createUniqueKey()
        gameBoard = GAME_BOARDS.get(gameKey, None)

        if not gameBoard:
            GAME_BOARDS[gameKey] = NetworkGame()
            break

    return gameKey

def cleanupGames():
    '''Remove any dead boards'''
    for gameKey, board in GAME_BOARDS.items():
        if time.time() - board.accessTime > REMOVAL_TIME:
            del GAME_BOARDS[gameKey]

def listGames():
    gameBoards = GAME_BOARDS.items()
    gameBoards.sort(lambda x, y: cmp(x[1], y[1]))

    buf = ''

    for gameKey, board in gameBoards:
        buf += "%s %d %s\n" % (time.strftime('%Y.%m.%d %H:%M:%S',
                                   time.localtime(board.accessTime)),
                               board.playerCount,
                               gameKey)

    return buf

def createUniqueKey():
    '''Build a random game key w/ a 16 bit md5 digest'''
    return md5.new(str(time.time()) + str(random.randint(0, 1000))).hexdigest()

def getBoard(gameKey):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        return gameBoard.board.asciiBoard()
    return None

def moveRow(gameKey, row, direction):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        gameBoard.board.moveRow(row, direction)
        return True
    return False

def moveColumn(gameKey, column, direction):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        gameBoard.board.moveColumn(column, direction)
        return True
    return False
    
def findPath(gameKey, start_column, start_row, end_column, end_row):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        tGraph = traverse.TraversalGraph(gameBoard.board)
        return str(tGraph.findPath(
            (start_column, start_row), (end_column, end_row)))
    return None


server = SimpleXMLRPCServer(('localhost', 8000))
print "Listening on port 8000"

server.register_function(newGame, "newGame")
server.register_function(listGames, "listGames")
server.register_function(getBoard, "getBoard")
server.register_function(moveRow, "moveRow")
server.register_function(moveColumn, "moveColumn")
server.register_function(findPath, "findPath")
server.serve_forever()
