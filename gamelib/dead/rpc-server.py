import time
import md5
import random
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import board
import traverse

GAME_BOARDS = {}

# 60 secs * 30 = 30 min
REMOVAL_TIME = 60 * 30

class NetworkGame(object):
    def __init__(self):
        self.board = board.Board()
        self.players = [None, None, None, None]
        self.started = False

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

    def addPlayer(self):
        assert self.getPlayerCount() <= len(self.players)
        for count, player in enumerate(self.players):
            if not player:
                self.addNotification('Player joined')
                self.players[count] = NetworkPlayer()
                return self.players[count].playerKey
        return None

    def addNotification(self, notification):
        for player in self.players:
            if player:
                player.notifications.append(notification)

    def startGame(self):
        self.board.createBoard(self.playerCount)

class NetworkPlayer(object):
    def __init__(self):
        self.playerKey = createUniqueKey()
        self.accessTime = time.time()
        self.notifications = []

def startGame(gameKey):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        gameBoard.startGame()

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

def updateGame(gameKey, playerKey):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        for player in gameBoard.players:
            if player.playerKey == playerKey and player.notifications:
                notifications = '\n'.join(player.notifications)
                player.notifications = []
                return notifications
            else:
                return ''
    return None

def listGames():
    gameBoards = GAME_BOARDS.items()
    gameBoards.sort(lambda x, y: cmp(x[1], y[1]))

    buf = ''

    for gameKey, board in gameBoards:
        buf += "%s %d %s %s\n" % (time.strftime('%Y.%m.%d %H:%M:%S',
                                     time.localtime(board.accessTime)),
                                  board.playerCount,
                                  str(board.started),
                                  gameKey)

    return buf

def joinGame(gameKey):
    gameBoard = GAME_BOARDS.get(gameKey, None)
    if gameBoard:
        playerKey = gameBoard.addPlayer()
        return playerKey
    return None

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
server.register_function(joinGame, "joinGame")
server.register_function(startGame, "startGame")
server.register_function(getBoard, "getBoard")
server.register_function(moveRow, "moveRow")
server.register_function(moveColumn, "moveColumn")
server.register_function(findPath, "findPath")
server.register_function(updateGame, "updateGame")
server.serve_forever()
