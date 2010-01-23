#
# network.py
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
import random
import errno

sys.path.append('../')
import events
import settings

import pyglet



def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

CLIENT_CHUNK_LEN = 4

# Process all of the TEXT_ strings in server into usable regular
# expressions

_TextStrings = [x for x in dir(server) if x.startswith('TEXT_')]
STRING_CACHE = {}

for textStrName in _TextStrings:
    buf = getattr(server, textStrName)
    buf = buf.replace('*', '\*')
    buf = buf.replace('(', '\(')
    buf = buf.replace(')', '\)')
    buf = buf.replace('%s', '(.*)')
    buf = buf.replace('%d', '(.*)')

    STRING_CACHE[textStrName] = buf

class ClientSocketHandler(object):

    TextFunctions = {
        STRING_CACHE['TEXT_SET_NICK'] : 'on_setNick',
        STRING_CACHE['TEXT_YOUR_TURN'] : 'on_playerTurn',
        STRING_CACHE['TEXT_PLAYER_STARTED_GAME'] : 'on_startGame',
        STRING_CACHE['TEXT_CURRENT_GAMES'] : 'on_listGames',
        STRING_CACHE['TEXT_JOIN_GAME'] : 'on_joinGame',
        STRING_CACHE['TEXT_DATA'] : 'on_boardData',
        STRING_CACHE['TEXT_PLAYER_NUMBER'] : 'on_playerSetup',
        STRING_CACHE['TEXT_TILE_ROTATED'] : 'on_tileRotated',
        STRING_CACHE['TEXT_PLAYER_PUSHED_TILE'] : 'on_tilePushed',
        STRING_CACHE['TEXT_PLAYER_ENDED_TURN'] : 'on_endTurn',
        STRING_CACHE['TEXT_PLAYER_MOVED'] : 'on_playerMoved',
        STRING_CACHE['TEXT_PLAYER_TOOK_OBJECT'] : 'on_playerTookObject',
    }

    def __init__(self, sock=None, blocking=True):
        self.blocking = blocking

        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.msg = ''
        self.chunk = ''

        self._msgLenChunk = ''
        self._msgChunk = ''

        self.IncomingQueue = []

        self.settings = settings.GameSettings()
        self.settings.client = self

        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.handleNetwork()
        self.consumeQueue()

    def handleNetwork(self):
        try:
            if len(self._msgLenChunk) < CLIENT_CHUNK_LEN:
                self._msgLenChunk += \
                    self.sock.recv(CLIENT_CHUNK_LEN - len(self._msgLenChunk))

        except socket.error, args:
            return

        if len(self._msgLenChunk) == CLIENT_CHUNK_LEN:
            try:
                if len(self._msgChunk) < int(self._msgLenChunk):
                    self._msgChunk += \
                        self.sock.recv(int(self._msgLenChunk) -
                                       len(self._msgChunk))

            except socket.error, args:
                return

        if self._msgChunk and len(self._msgChunk) == int(self._msgLenChunk):
            self.IncomingQueue.append(self._msgChunk)
            self._msgChunk = ''
            self._msgLenChunk = ''

    def consumeQueue(self):
        for count in range(len(self.IncomingQueue)):
            msg = self.IncomingQueue[count]
            if msg.startswith('***'):
                for textStr in self.TextFunctions.keys():
                    mObj = re.match(textStr, msg)
                    if mObj:
                        events.fireEvent(self.TextFunctions[textStr],
                                         mObj.groups())

        self.IncomingQueue = []

    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
        except socket.error, args:
            if self.blocking and args[0] == errno.EINPROGRESS:
                pass

    def send(self, msg):
        totalSent = 0
        while totalSent < len(msg):
            sent = self.sock.send(msg[totalSent:])
            if sent == 0:
                raise RuntimeError, "socket connection broken"

            totalSent += sent

    def receive(self, retry=False):
        pass

    def waitForMessage(self, waitMsg):
        pass


class ClientBaseHandler(ClientSocketHandler):
    def __init__(self,
                 host='localhost',
                 port=server.port,
                 nick='foobar',
                 blocking=False):

        ClientSocketHandler.__init__(self, blocking=blocking)
        self.sock.setblocking(int(blocking))

        self.playerNumber = 0

        events.addListener(self)

        self.connect(host, port)
        self.setNick(nick)

        self.settings.board = board.Board()
        self.startLocation = (-1, -1)

    def on_startGame(self, args):
        playerNick = args[0]
        print "!!! Game started by %s" % playerNick
        self.send('/data')

    def setNick(self, nick):
        self.send('/nick %s\n' % nick)

    def on_setNick(self, args):
        nick = args[0]
        print "!!! Nick changed to %s" % nick
        self.nick = nick

    def on_listGames(self, args):
        gamelist = args[0]
        print "!!! Gamelist: %s" % gamelist

        if not gamelist:
            print "No games"
            return

        if self.settings.joinFirstGame:

            for game in gamelist.split('\n'):
                gameId, players = game.split()

                self.send('/join %s' % gameId)
                break

    def on_joinGame(self, args):
        gameNumber = args[0]
        print "!!! Player joined game %s" % gameNumber

    def joinFirstGame(self):
        print "Join first game"

        self.settings.joinFirstGame = True
        self.send('/list')


    def getPlayerNumber(self):
        playerText = re.sub(r'\(', '\(', server.TEXT_PLAYER_NUMBER)
        playerText = re.sub(r'\)', '\)', playerText)
        playerText = re.sub(r'%d', '(\d)', playerText)
        playerText = re.sub('\*', '\*', playerText)

        while True:
            msg = self.receive()
            mObj = re.match(playerText, msg)
            if mObj:
                playerNumber = int(mObj.groups()[0])
                location = \
                    (int(mObj.groups()[1]), int(mObj.groups()[2]))
                break

        print "Player number = %d" % playerNumber
        print "Starting Location = " + str(location)
        self.playerNumber = playerNumber
        self.startLocation = location

        if playerNumber == 1:
            self.waitForTurn()

    def pushTile(self, direction, num):
        print "pushing %d %d" % (num, direction)
        if direction in [board.NORTH, board.SOUTH]:
            self.send('/pushcolumn %d %d' % (num, direction))
        elif direction in [board.EAST, board.WEST]:
            self.send('/pushrow %d %d' % (num, direction))
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
            print msg

    def getData(self):
        self.send('/data')
        boardData = self.receive()
        print boardData

        self.board.deserialize(boardData)

        print self.board.asciiBoard()
        print self.board.players[self.playerNumber-1].getAsciiItemsRemaining()

    def moveToTile(self, column, row):
        location = self.board.players[self.playerNumber-1].location
        print "moving from %d %d to %d %d" % \
            (location[0], location[1], column, row)
        self.send('/move %d %d' % (column, row))

        self.waitForMessage(server.TEXT_PLAYER_MOVED % (self.nick, column, row))
        print "Moved to (%d, %d)" % (column, row)

    def endTurn(self):
        print "End the turn"
        self.send('/end')

    def rotateTile(self):
        print "rotating tile"
        self.send('/rotate 1')

        self.waitForMessage(server.TEXT_PLAYER_ROTATED_TILE)
        print "rotated"



