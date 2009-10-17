#
# ai.py
# (c) 2009 pdevine@sonic.net
# Bombitron - www.bombitron.com
#
#

import sys
import re

import socket
import server
import board
import traverse

MSGLEN = 4096

def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

class AISocketHandler(object):
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        totalSent = 0
        while totalSent < len(msg):
            sent = self.sock.send(msg[totalSent:])
            if sent == 0:
                raise RuntimeError, "socket connection broken"

            totalSent += sent

    def receive(self):
        msg = ''
        msgLen = ''
 
        while len(msgLen) < 4:
            msgLenChunk = self.sock.recv(4)
            if msgLenChunk == '':
                raise RuntimeError, "socket connection broken"

            msgLen += msgLenChunk

        while len(msg) < int(msgLen):
            chunk = self.sock.recv(int(msgLen))
            msg += chunk
            
        return msg

class AIBaseClass(AISocketHandler):
    def __init__(self, host='localhost', port=server.port, nick='foobar'):
        AISocketHandler.__init__(self)
        self.playerNumber = 0

        self.connect(host, port)
        self.setNick(nick)

        self.board = board.Board()

    def waitForMessage(self, waitMsg):
        while True:
            msg = self.receive()
            if msg == waitMsg:
                return

    def setNick(self, nick):
        self.send('/nick %s' % nick)

        self.waitForMessage(server.TEXT_SET_NICK % nick)
        print "Nick set to %s" % nick

        self.nick = nick

    def joinFirstGame(self):
        self.send('/list')

        games = self.receive()

        # XXX - this will need to change if the /list command
        #       changes what it returns

        if games != '':
            game = games.split('\n')[0]
            gameKey, totalPlayers = game.split()
        else:
            print "no game to join"

        self.joinGame(gameKey)

    def joinGame(self, gameKey):
        self.send('/join %s' % gameKey)

        self.waitForMessage(server.TEXT_JOIN_GAME % gameKey)
        print "Joined game %s" % gameKey

    def getPlayerNumber(self):
        playerText = re.sub('%d', '(\d)', server.TEXT_PLAYER_NUMBER)
        playerText = re.sub('\*', '\*', playerText)

        while True:
            msg = self.receive()
            mObj = re.match(playerText, msg)
            if mObj:
                playerNumber = int(mObj.groups()[0])
                break

        print "Player number = %d" % playerNumber
        self.playerNumber = playerNumber

    def waitForTurn(self):
        self.waitForMessage(server.TEXT_YOUR_TURN)
        print "Our turn"

    def pushTile(self, direction, num):
        if direction in [board.NORTH, board.SOUTH]:
            self.send('/pushcolumn %d %d' % (direction, num))
        elif direction in [board.EAST, board.WEST]:
            self.send('/pushrow %d %d' % (direction, num))
        else:
            print "Couldn't push tile"

        pushedText = re.sub('%s', '(\w+)', server.TEXT_PLAYER_PUSHED_TILE)
        pushedText = re.sub('\*', '\*', pushedText)

        msg = self.receive()
        mObj = re.match(pushedText, msg)
        if mObj:
            print "Pushed tile"
        else:
            print "Uh-oh.  Tile not pushed"

    def getData(self):
        self.send('/data')
        boardData = self.receive()
        print boardData

        self.board.deserialize(boardData)

        print self.board.asciiBoard()
        print self.board.players[self.playerNumber-1].getAsciiItemsRemaining()

    def moveToAnyItem(self):
        aiPlayer = self.board.players[self.playerNumber-1]

        traverseGraph = traverse.TraversalGraph(self.board)

        for rowCount, row in enumerate(self.board.board):
            for columnCount, tile in enumerate(row):
                tileLocation = (columnCount, rowCount)
                if tile.boardItem in aiPlayer.boardItems and \
                   not tile.boardItem.found:
                    if traverseGraph.findPath(aiPlayer.location, tileLocation):
                        self.moveToTile(*tileLocation)
                        return

        print "Couldn't find item"

    def moveToTile(self, column, row):
        self.send('/move %d %d' % (column, row))

        self.waitForMessage(server.TEXT_PLAYER_MOVED % (self.nick, column, row))
        print "Moved to (%d, %d)" % (column, row)
        
    def endTurn(self):
        print "End the turn"
        self.send('/end')


sys.excepthook = debug

ai = AIBaseClass()
ai.joinFirstGame()
ai.getPlayerNumber()
while True:
    ai.waitForTurn()
    ai.getData()
    ai.pushTile(1, 4)
    ai.moveToAnyItem()
    ai.endTurn()
ai.sock.close()

