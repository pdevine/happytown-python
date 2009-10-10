#
# server.py
# (c) 2009 pdevine@sonic.net
# Bombitron - www.bombitron.com
#
#

import select
import socket
import sys
import md5
import time
import random
import string

import board

host = ''
port = 50001
backlog = 5
size = 1024

TIMEOUT = 5

VALID_CHARS = string.ascii_letters + string.digits
NICK_LENGTH = 10

ERROR_JOIN_GAME = 'ERROR: need to join a game\n'
ERROR_START_GAME = 'ERROR: need to start the game\n'
ERROR_ROTATE_DIRECTION = 'ERROR: need a direction to rotate\n'
ERROR_ROW_DIRECTION = 'ERROR: need to specify a row and direction\n'
ERROR_COLUMN_DIRECTION = 'ERROR: need to specify a column and direction\n'
ERROR_COLUMN_ROW = 'ERROR: need to specify a column and row\n'
ERROR_NICK_CHARS = 'ERROR: name must be ascii letters and numbers\n'
ERROR_JOIN_GAME = 'ERROR: need to join or create a new game\n'
ERROR_UNKNOWN_COMMAND = 'ERROR: unknown command %s\n'
ERROR_SPECIFY_NICK = 'ERROR: need to specify a nick name\n'
ERROR_SPECIFY_GAME = 'ERROR: need to specify a game to join\n'
ERROR_NICK_MAX_CHARS = 'ERROR: nick name must be less than %d\n'
ERROR_EXISTING_NICK = 'ERROR: that nick name is already taken\n'
ERROR_UNKNOWN_NICK_CREATE = \
    'ERROR: you must specify a nick before creating a new game\n'
ERROR_UNKNOWN_NICK_START = \
    'ERROR: you must specify a nick before starting a new game\n'
ERROR_UNKNOWN_GAME = 'ERROR: game %s does not exist\n'
ERROR_GAME_JOINED = 'ERROR: already joined a game\n'
ERROR_NEED_PLAYERS = 'ERROR: need more players to start the game\n'
ERROR_GAME_STARTED = 'ERROR: game already started\n'

TEXT_SET_NICK = "*** You are now known as %s\n"
TEXT_JOIN_GAME = "*** You have joined game %s\n"

gameBoards = {}
clientDict = {}

def listGames(client, *args):
    buf = []
    for game in gameBoards.keys():
        buf.append('%s %d' % (game, gameBoards[game].playerCount))
    return '\n'.join(buf) + '\n'

def joinGame(client, *args):
    #assert args[0] in gameBoards.keys()

    if client.name == 'Unknown':
        return ERROR_UNKNOWN_NICK_START

    if not args:
        return ERROR_SPECIFY_GAME

    gameKey = args[0]

    if client.game and hasattr(client.game, 'board'):
        return ERROR_GAME_JOINED

    if gameKey not in gameBoards.keys():
        return ERROR_UNKNOWN_GAME % gameKey

    if hasattr(gameBoards[gameKey].board, 'board'):
        return ERROR_GAME_STARTED

    if not gameBoards[gameKey].addPlayer(client):
        return ERROR_JOIN_GAME
    else:
        client.game = gameBoards[gameKey]

        buf = '%s has joined the game.' % client.name
        notifyPlayers(client, buf)

    return TEXT_JOIN_GAME % gameKey

def leaveGame(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    buf = '%s has left the game.' % client.name
    notifyPlayers(client, buf)

    # XXX - need to make a call out to the board to tell it that we're no
    #       longer joined -- this could result in the game being won

    client.game.players.remove(client)
    cleanupGame(client.game.gameKey)
    client.game = None

def cleanupGame(gameKey):
    game = clientDict.get(gameKey)

    if game:
        for player in game.players:
            if player:
                return

    del gameBoards[gameKey]

def setNick(client, *args):
    if not args:
        return ERROR_SPECIFY_NICK
    elif len(args[0]) > NICK_LENGTH:
        return ERROR_NICK_MAX_CHARS % NICK_LENGTH

    oldName = client.name
    newName = args[0]

    for c in newName:
        if c not in VALID_CHARS:
            return ERROR_NICK_CHARS

    if lookupNick(newName):
        return ERROR_EXISTING_NICK

    client.name = newName
    buf = '%s changed nick to %s' % (oldName, client.name)
    notifyAllPlayers(buf)

    return TEXT_SET_NICK % client.name
    
def lookupNick(nick):
    for client in clientDict.keys():
        if clientDict[client].name == nick:
            return clientDict[client]
    return None

def startGame(client, *args):
    # XXX - only allow starting by the person who created the game?

    if not client.game:
        return ERROR_JOIN_GAME

    if hasattr(client.game.board, 'board'):
        return ERROR_GAME_STARTED

    try:
        client.game.board.createBoard(client.game.playerCount)
    except board.BoardCreationError, msg:
        return ERROR_NEED_PLAYERS

    buf = '%s has started the game.' % client.name
    notifyPlayers(client, buf)

    # the player who starts the game isn't always the player whose turn
    # it is first
    notifyPlayer(client, client.game.board.playerTurn, "It's your turn")

    return ''

def newGame(client, *args):
    global gameBoards

    if client.name == 'Unknown':
        return ERROR_UNKNOWN_NICK_CREATE

    if hasattr(client, 'game') and hasattr(client.game, 'board'):
        return ERROR_GAME_JOINED

    while True:
        gameKey = createUniqueKey()
        gameBoard = gameBoards.get(gameKey, None)

        if not gameBoard:
            gameBoards[gameKey] = NetworkGame(gameKey)
            break

    buf = "%s has created new game %s" % (client.name, gameKey)
    notifyAllPlayers(buf)

    joinGame(client, gameKey)

    return gameKey + '\n'

def printAsciiBoard(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    return client.game.board.asciiBoard()

def printFloatingTile(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    return client.game.board.floatingTile.asciiTile()

def printHelp(client, *args):
    return 'XXX - Not Implemented\n'

def listUsers(client, *args):
    buf = []
    for userKey in clientDict.keys():
        user = clientDict[userKey]
        if user.game:
            buf.append('%s : %s' % (user.name, user.game.gameKey))
        else:
            buf.append('%s : No Game' % user.name)

    return '\n'.join(buf) + '\n'

def rotateFloatingTile(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    if len(args) != 1:
        return ERROR_ROTATE_DIRECTION

    try:
        if args[0].lower() in ['1', 'clockwise', 'clock']:
            client.game.board.floatingTile.rotateClockwise()
        elif args[0].lower in ['2', 'counterclockwise', 'counter']:
            client.game.board.floatingTile.rotateCounterClockwise()
    except:
        # XXX - shouldn't be able to rotate out of turn
        pass

    return ''

def printBoard(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    return client.game.board.serialize()

def moveRow(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    if len(args) != 2:
        return ERROR_ROW_DIRECTION

    try:
        row = int(args[0])
        dir = int(args[1])
    except ValueError:
        return ERROR_ROW_DIRECTION

    try:
        client.game.board.moveRow(client.getPlayerNumber(), row, dir)
    except board.BoardMovementError, msg:
        return "ERROR: %s\n" % str(msg)

    buf = "%s pushed the floating tile" % client.name
    notifyPlayers(client, buf)

    return ''

def moveColumn(client, *args):
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    if len(args) != 2:
        return ERROR_COLUMN_DIRECTION

    try:
        col = int(args[0])
        dir = int(args[1])
    except ValueError:
        return ERROR_COLUMN_DIRECTION

    try:
        client.game.board.moveColumn(client.getPlayerNumber(), col, dir)
    except board.BoardMovementError, msg:
        return "ERROR: %s\n" % str(msg)

    buf = "%s pushed the floating tile" % client.name
    notifyPlayers(client, buf)

    return ''

def notifyPlayers(client, msg):
    for player in client.game.players:
        if player:
            player.send("*** %s\n" % msg)

def notifyPlayer(client, player, msg):
    client.game.players[player-1].send("*** %s\n" % msg)

def notifyAllPlayers(msg):
    for client in clientDict.keys():
        clientDict[client].send("*** %s\n" % msg)


def movePlayer(client, *args):

    if len(args) != 2:
        return ERROR_COLUMN_ROW

    try:
        col = int(args[0])
        row = int(args[1])
    except ValueError:
        return ERROR_COLUMN_ROW

    try:
        client.game.board.movePlayer(client.getPlayerNumber(), col, row)
    except board.PlayerMovementError, msg:
        return "ERROR: %s\n" % str(msg)

    buf = "%s moved to (%d, %d)" % (client.name, col, row)
    notifyPlayers(client, buf)

    return ''

def endTurn(client, *args):
    try:
        client.game.board.endTurn(client.getPlayerNumber())
    except board.PlayerTurnError, msg:
        return "ERROR: %s\n" % str(msg)

    buf = "%s ended the turn" % client.name
    notifyPlayers(client, buf)

    notifyPlayer(client, client.game.board.playerTurn, "It's your turn")

    return ''

class NetworkGame(object):
    def __init__(self, gameKey):
        self.board = board.Board()
        self.players = [None, None, None, None]
        self.started = False
        self.gameKey = gameKey

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

    def addPlayer(self, networkPlayer):
        assert self.playerCount <= len(self.players)

        addedPlayer = False

        for count, player in enumerate(self.players):
            if not player:
                self.players[count] = networkPlayer
                addedPlayer = True
                break

        return addedPlayer


def createUniqueKey():
    '''Build a random game key w/ a 16 bit md5 digest'''
    return md5.new(str(time.time()) + str(random.randint(0, 1000))).hexdigest()

class NetworkPlayer(object):
    def __init__(self, name, client, address):
        self.name = name
        self.client = client
        self.address = address

        self.game = None

    def getPlayerNumber(self):
        assert self.game.board

        count = 1
        for player in self.game.players:
            if player == self:
                return count

            count += 1

        return -1

    def send(self, msg):
        self.client.send('%04d' % len(msg) + msg)


def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

commandDict = {
    '/list' : listGames,
    '/users' : listUsers,
    '/join' : joinGame,
    '/nick' : setNick,
    '/new' : newGame,
    '/start' : startGame,
    '/leave' : leaveGame,
    '/asciiboard' : printAsciiBoard,
    '/board' : printBoard,
    '/pushrow' : moveRow,
    '/pushcolumn' : moveColumn,
    '/move' : movePlayer,
    '/end' : endTurn,
    '/ft' : printFloatingTile,
    '/rotate' : rotateFloatingTile,
    '/help' : printHelp,
}

def main():

    sys.excepthook = debug

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            print "Starting server on %s %d" % (host, port)
            server.bind((host, port))
        except:
            print "Port in use.  Trying again in %d seconds." % TIMEOUT
            time.sleep(TIMEOUT)
        else:
            break

    server.listen(backlog)

    input = [server, sys.stdin]
    output = []

    running = True
    playerCount = 0

    while running:
        inputready, outputready, exceptready = select.select(input, [], [])

        for sock in inputready:
            if sock == server:
                client, address = server.accept()
                input.append(client)
                output.append(client)
                clientDict[client] = NetworkPlayer('Unknown', client, address)
                buf = "%s joined (%s)\n" % (clientDict[client].name, address[0])
                print buf.rstrip()

            elif sock == sys.stdin:
                sys.stdin.readline()
                running = False

            else:
                data = sock.recv(size)
                if data:
                    # all commands start with /
                    if data.startswith('/'):
                        tokens = data.split()
                        print tokens
                        cmd = commandDict.get(tokens[0])
                        if cmd:
                            buf = cmd(clientDict[sock], *tokens[1:])
                            if buf:
                                try:
                                    sock.send('%04d' % len(buf) + buf)
                                except:
                                    buf = "%s left\n" % clientDict[sock].name
                                    input.remove(sock)
                                    del clientDict[sock]
                        else:
                            buf = ERROR_UNKNOWN_COMMAND % tokens[0]
                            try:
                                sock.send('%04f' % len(buf) + buf)
                            except:
                                buf = "%s left\n" % clientDict[sock].name
                                input.remove(sock)
                                del clientDict[sock]
                else:
                    buf = "%s left\n" % clientDict[sock].name
                    sock.close()
                    input.remove(sock)
                    del clientDict[sock]
                    print buf.rstrip()

    server.close()

if __name__ == '__main__':
    main()

