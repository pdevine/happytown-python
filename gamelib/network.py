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

def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

class ClientSocketHandler(object):
    def __init__(self, sock=None):
        self.blocking = True

        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.msg = ''
        self.chunk = ''

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

    def receive(self):
        if self.blocking:
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
        else:
            try:
                msgLenChunk = self.sock.recv(4)
                print '[' + msgLenChunk + ']'
                if len(msgLenChunk) == 4:
                    msg = self.sock.recv(int(msgLenChunk))
                    if len(msg) == int(msgLenChunk):
                        return msg
            except socket.error, args:
                # XXX - 35 = resource temp unavailable
                if args[0] == 35:
                    pass

    def waitForMessage(self, waitMsg):
        while True:
            msg = self.receive()
            if msg == waitMsg:
                return


class ClientBaseHandler(ClientSocketHandler):
    def __init__(self,
                 host='localhost',
                 port=server.port,
                 nick='foobar',
                 blocking=False):

        ClientSocketHandler.__init__(self)
        self.sock.setblocking(int(blocking))

        self.playerNumber = 0
        self.blocking = blocking

        self.connect(host, port)
        self.setNick(nick)

        self.board = board.Board()
        self.startLocation = (-1, -1)

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

