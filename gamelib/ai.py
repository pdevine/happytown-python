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
import random

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
        self.startLocation = (-1, -1)

    def waitForMessage(self, waitMsg):
        while True:
            msg = self.receive()
            if msg == waitMsg:
                return

    def setNick(self, nick):

        for count in range(1, 5):
            self.send('/nick %s' % nick)
            while True:
                msg = self.receive()

                if msg == server.TEXT_SET_NICK % nick:
                    print "Nick set to %s" % nick
                    self.nick = nick
                    return
                elif msg == server.ERROR_EXISTING_NICK:
                    break
            nick += str(count)

        print "Couldn't set nick!"

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

    def waitForTurn(self):
        self.waitForMessage(server.TEXT_YOUR_TURN)
        print "Our turn"

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

    def searchForAnyItem(self):

        for direction in [board.WEST, board.EAST, board.NORTH, board.SOUTH]:
            for num in range(1,
               max(self.board.rows-1, self.board.columns-1)):

                if direction in [board.WEST, board.EAST] and \
                   num > self.board.rows-1:
                    continue
                elif direction in [board.NORTH, board.SOUTH] and \
                   num > self.board.columns-1:
                    continue
                else:
                    # wtf?
                    pass

                # we could be more crafty about not sliding tiles in
                # here which aren't going to connect to anything but
                # that might be inefficient as well

                for rotation in range(4):
                    self.board.floatingTilePushed = False

                    for rotateCount in range(rotation):
                        self.board.floatingTile.rotateClockwise()

                    if direction in [board.WEST, board.EAST]:
                        self.board.moveRow(self.playerNumber, num, direction)
                    elif direction in [board.NORTH, board.SOUTH]:
                        self.board.moveColumn(self.playerNumber, num, direction)

                    items = self.buildItemList(self.playerNumber)

                    traverseGraph = traverse.TraversalGraph(self.board)
                    location = self.board.players[self.playerNumber-1].location

                    for item in items:
                        if traverseGraph.findPath(location, item):
                            print "found item"
                            for rotateCount in range(rotation):
                                self.rotateTile()
                            self.pushTile(direction, num)
                            self.moveToTile(*item)
                            return

                    # push the row/col back where it was --
                    # this is faster than making a new copy of the board
                    self.board.floatingTilePushed = False

                    if direction in [board.WEST, board.EAST]:
                        print "push row %d %d" % \
                            (num, board.OPP_DICT[direction])
                        self.board.moveRow(self.playerNumber,
                                           num,
                                           board.OPP_DICT[direction])
                    elif direction in [board.NORTH, board.SOUTH]:
                        print "push column %d %d" % \
                            (num, board.OPP_DICT[direction])
                        self.board.moveColumn(self.playerNumber,
                                              num,
                                              board.OPP_DICT[direction])

                    for rotateCount in range(rotation):
                        self.board.floatingTile.rotateCounterClockwise()


        # give up and just push any tile
        print "Couldn't find an item"
        if random.randint(0, 1):
            self.pushTile(random.choice([board.EAST, board.WEST]),
                          random.randint(1, self.board.rows-2))
        else:
            self.pushTile(random.choice([board.NORTH, board.SOUTH]),
                          random.randint(1, self.board.columns-2))


    def moveToAnyItem(self):
        items = self.buildItemList(self.playerNumber-1)
        location = self.board.players[self.playerNumber-1].location

        if not items:
            # XXX - move home?
            print "No items found"
            pass

        else:
            
            traverseGraph = traverse.TraversalGraph(self.board)

            for item in items:
                if traverseGraph.findPath(location, item):
                    self.moveToTile(*item)
                    return
            print "Couldn't move to an item"

    def buildItemList(self, playerNumber):
        items = []

        player = self.board.players[playerNumber-1]

        for rowCount, row in enumerate(self.board.board):
            for columnCount, tile in enumerate(row):
                tileLocation = (columnCount, rowCount)
                if tile.boardItem in player.boardItems and \
                   not tile.boardItem.found:
                    items.append(tileLocation)

        if not items:
            print "Going home"
            items = [self.startLocation]

        return items

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

sys.excepthook = debug

ai = AIBaseClass()
ai.joinFirstGame()
ai.getPlayerNumber()
while True:
    ai.waitForTurn()
    ai.getData()
    ai.searchForAnyItem()
    ai.endTurn()
ai.sock.close()

