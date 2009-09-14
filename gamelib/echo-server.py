
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
    assert args[0] in gameBoards.keys()

    gameBoards[args[0]].addPlayer(client)
    client.game = gameBoards[args[0]]

    return 'joined game %s' % args[0]

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
    return client.game.board.asciiBoard()

def printBoard(client, *args):
    return client.game.board.serialize()

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
            for player in self.players:
                player.send('%s has joined the game.' % networkPlayer.name)

def createUniqueKey():
    '''Build a random game key w/ a 16 bit md5 digest'''
    return md5.new(str(time.time()) + str(random.randint(0, 1000))).hexdigest()

class NetworkPlayer(object):
    def __init__(self, name, client, address):
        self.name = name
        self.client = client
        self.address = address

        self.game = None

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
                            sock.send(cmd(clientDict[client], *tokens[1:]))
                else:
                    buf = "%s left\n" % clientDict[sock].name
                    sock.close()
                    input.remove(sock)
                    del clientDict[sock]
                    print buf.rstrip()

    server.close()

main()
