
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

gameBoards = {}
clientDict = {}

def listGames(client, *args):
    buf = []
    for game in gameBoards.keys():
        buf.append('%s %d' % (game, gameBoards[game].playerCount))
    return '\n'.join(buf) + '\n'

def joinGame(client, *args):
    #assert args[0] in gameBoards.keys()

    if args[0] not in gameBoards.keys():
        return 'game %s does not exist\n' % (args[0])

    gameBoards[args[0]].addPlayer(client)
    client.game = gameBoards[args[0]]

    return 'joined game %s\n' % args[0]

def setNick(client, *args):
    if not args:
        return 'need to specify a name\n'
    elif len(args[0]) > NICK_LENGTH:
        return 'name must be less than %d\n' % NICK_LENGTH
        
    for c in args[0]:
        if c not in VALID_CHARS:
            return 'name must be ascii letters and numbers\n'

    client.name = args[0] 
    return 'name changed to %s\n' % (client.name)

def startGame(client, *args):
    # XXX - only allow starting by the person who created the game?

    if not client.game:
        return 'need to join a game\n'

    client.game.board.createBoard(client.game.playerCount)

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
        return 'need to join a game\n'

    if not client.game.board:
        return 'need to start the game\n'

    return client.game.board.asciiBoard()

def printFloatingTile(client, *args):
    if not client.game:
        return 'need to join a game\n'

    if not client.game.board:
        return 'need to start the game\n'

    return client.game.board.floatingTile.asciiTile()


def rotateFloatingTile(client, *args):
    if len(args) != 1:
        return 'need a direction to rotate\n'

    if args[0] == '1':
        client.game.board.floatingTile.rotateClockwise()
    elif args[0] == '2':
        client.game.board.floatingTile.rotateCounterClockwise()

    return ''

def printBoard(client, *args):
    if not client.game: 
        return 'need to join a game\n'

    if not client.game.board:
        return 'need to start the game\n'

    return client.game.board.serialize()

def moveRow(client, *args):
    if not client.game: 
        return 'need to join a game\n'

    if not client.game.board:
        return 'need to start the game\n'

    if len(args) != 2:
        return 'need to specify a row and direction'

    try:
        row = int(args[0])
        dir = int(args[1])
    except ValueError:
        return 'need to specify a row and direction'

    #return str(client.getPlayerNumber()) + '\n'
    print "player %d pushed row" % client.getPlayerNumber()
    print client
    try:
        client.game.board.moveRow(client.getPlayerNumber(), row, dir)
    except board.BoardMovementError, msg:
        return str(msg) + '\n'

    buf = "%s pushed the floating tile" % client.name
    notifyBoardChanged(client, buf)

    return ''

def moveColumn(client, *args):
    if not client.game: 
        return 'need to join a game\n'

    if not client.game.board:
        return 'need to start the game\n'

    if len(args) != 2:
        return 'need to specify a column and direction'

    try:
        col = int(args[0])
        dir = int(args[1])
    except ValueError:
        return 'need to specify a column and direction'

    try:
        client.game.board.moveColumn(client.getPlayerNumber(), col, dir)
    except board.BoardMovementError, msg:
        return str(msg) + '\n'

    buf = "%s pushed the floating tile" % client.name
    notifyBoardChanged(client, buf)

    return ''

def notifyBoardChanged(client, msg):
    for player in client.game.players:
        if player:
            player.send(msg + "\n")


def movePlayer(client, *args):

    if len(args) != 2:
        return 'need to specify a row and column\n'

    try:
        col = int(args[0])
        row = int(args[1])
    except ValueError:
        return 'need to specify a column and row\n'

    try:
        client.game.board.movePlayer(client.getPlayerNumber(), col, row)
    except board.PlayerMovementError, msg:
        return str(msg) + '\n'

    return ''

def endTurn(client, *args):
    try:
        client.game.board.endTurn(client.getPlayerNumber())
    except board.PlayerTurnError, msg:
        return str(msg) + '\n'

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

        for count, player in enumerate(self.players):
            if not player:
                self.players[count] = networkPlayer
                break

        if not count:
            return None
        else:
            buf = '%s has joined the game.\n' % networkPlayer.name
            for player in self.players:
                if player:
                    player.send(buf)

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
                            sock.send('Unknown command %s\n' % tokens[0])
                else:
                    buf = "%s left\n" % clientDict[sock].name
                    sock.close()
                    input.remove(sock)
                    del clientDict[sock]
                    print buf.rstrip()

    server.close()

main()
