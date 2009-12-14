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
import network

def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

class AIBaseClass(network.ClientBaseHandler):
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

    def waitForTurn(self):
        self.waitForMessage(server.TEXT_YOUR_TURN)
        print "Our turn"

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
                        print "push row %d %d" % (num, direction)
                        self.board.moveRow(self.playerNumber, num, direction)
                    elif direction in [board.NORTH, board.SOUTH]:
                        print "push col %d %d" % (num, direction)
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

sys.excepthook = debug

ai = AIBaseClass(blocking=False)
ai.joinFirstGame()
ai.getPlayerNumber()
while True:
    ai.waitForTurn()
    ai.getData()
    ai.searchForAnyItem()
    ai.endTurn()
ai.sock.close()

