
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


gameBoards = {}
clientDict = {}

def listGames(client, *args):
    buf = []
    for game in gameBoards.keys():
        buf.append('%s %d' % (game, gameBoards[game].playerCount))
    return '\n'.join(buf) + '\n'

def joinGame(client, *args):
    #assert args[0] in gameBoards.keys()

    print "joining game"
    if args[0] not in gameBoards.keys():
        return 'game %s does not exist\n' % (args[0])

    if not gameBoards[args[0]].addPlayer(client):
        print "couldn't join"
        return ERROR_JOIN_GAME
    else:
        print "trying to join"
        client.game = gameBoards[args[0]]
        print gameBoards[args[0]]

        buf = '%s has joined the game.' % client.name
        notifyPlayers(client, buf)

    return ''

def setNick(client, *args):
    if not args:
        return 'need to specify a name\n'
    elif len(args[0]) > NICK_LENGTH:
        return 'name must be less than %d\n' % NICK_LENGTH
        
    for c in args[0]:
        if c not in VALID_CHARS:
            return ERROR_NICK_CHARS

    client.name = args[0] 
    return 'name changed to %s\n' % (client.name)

def startGame(client, *args):
    # XXX - only allow starting by the person who created the game?

    if not client.game:
        return ERROR_JOIN_GAME

    client.game.board.createBoard(client.game.playerCount)

    buf = '%s has started the game.' % client.name
    notifyPlayers(client, buf)

    return ''

def newGame(client, *args):
    global gameBoards

    while True:
        gameKey = createUniqueKey()
        gameBoard = gameBoards.get(gameKey, None)

        if not gameBoard:
            gameBoards[gameKey] = NetworkGame()
            break

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

    #return str(client.getPlayerNumber()) + '\n'
    print "player %d pushed row" % client.getPlayerNumber()
    print client
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
    def __init__(self):
        self.board = board.Board()
        self.players = [None, None, None, None]
        self.started = False

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
        self.client.send(msg)


def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

commandDict = {
    '/list' : listGames,
    '/join' : joinGame,
    '/nick' : setNick,
    '/new' : newGame,
    '/start' : startGame,
    '/asciiboard' : printAsciiBoard,
    '/board' : printBoard,
    '/pushrow' : moveRow,
    '/pushcolumn' : moveColumn,
    '/move' : movePlayer,
    '/end' : endTurn,
    '/ft' : printFloatingTile,
    '/rotate' : rotateFloatingTile,
}

def main():

    sys.excepthook = debug

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
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
                print client
                print clientDict

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
                            sock.send(cmd(clientDict[sock], *tokens[1:]))
                        else:
                            sock.send(ERROR_UNKNOWN_COMMAND % tokens[0])
                else:
                    buf = "%s left\n" % clientDict[sock].name
                    sock.close()
                    input.remove(sock)
                    del clientDict[sock]
                    print buf.rstrip()

    server.close()

main()
