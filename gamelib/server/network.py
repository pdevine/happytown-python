from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor

import string
import hashlib
import time
import random

import sys
sys.path.append('..')

import board

PORT = 50001

#
# Server specific error strings
#
# These are errors specific to the server.  Play errors are raised in the
# board.py module.
#
#

ERROR_JOIN_GAME = 'ERROR: need to join a game\r\n'
ERROR_START_GAME = 'ERROR: need to start the game\r\n'
ERROR_ROTATE_DIRECTION = 'ERROR: need a direction to rotate\r\n'
ERROR_ROW_DIRECTION = 'ERROR: need to specify a row and direction\r\n'
ERROR_COLUMN_DIRECTION = 'ERROR: need to specify a column and direction\r\n'
ERROR_COLUMN_ROW = 'ERROR: need to specify a column and row\r\n'
ERROR_NICK_CHARS = 'ERROR: name must be ascii letters and numbers\r\n'
ERROR_JOIN_GAME = 'ERROR: need to join or create a new game\r\n'
ERROR_UNKNOWN_COMMAND = 'ERROR: unknown command %s\r\n'
ERROR_SPECIFY_NICK = 'ERROR: need to specify a nick name\r\n'
ERROR_SPECIFY_GAME = 'ERROR: need to specify a game to join\r\n'
ERROR_SPACES_IN_NICK = 'ERROR: nick name must not contain spaces\r\n'
ERROR_NICK_MIN_CHARS = 'ERROR: nick name must be more than %d characters\r\n'
ERROR_NICK_MAX_CHARS = 'ERROR: nick name must be less than %d characters\r\n'
ERROR_NICK_EXISTS = 'ERROR: that nick name is already taken\r\n'
ERROR_NICK_IS_SAME = 'ERROR: you have already set your nick to %s\r\n'
ERROR_UNKNOWN_NICK_CREATE = \
    'ERROR: you must specify a nick before creating a new game\r\n'
ERROR_UNKNOWN_NICK_START = \
    'ERROR: you must specify a nick before starting a new game\r\n'
ERROR_UNKNOWN_GAME = 'ERROR: game %s does not exist\r\n'
ERROR_GAME_JOINED = 'ERROR: already joined a game\r\n'
ERROR_NEED_PLAYERS = 'ERROR: need more players to start the game\r\n'
ERROR_GAME_STARTED = 'ERROR: game already started\r\n'
ERROR_NOT_PERMITTED = 'ERROR: you are not permitted to do that\r\n'

NICK_UNKNOWN_NAME = 'Unknown'
NICK_MIN_LENGTH = 3
NICK_MAX_LENGTH = 14
NICK_VALID_CHARS = string.ascii_letters + string.digits

#
# Server event text strings
#
# These are text strings which can be returned by the server.  They can
# be used to trigger AI actions.
#

TEXT_SET_NICK = "*** You are now known as %s\r\n"
TEXT_JOIN_GAME = "*** You have joined game %s\r\n"
TEXT_YOUR_TURN = "*** It's your turn\r\n"
TEXT_YOU_WIN = "*** You won the game!\r\n"
TEXT_PLAYER_WON = "*** %s has won the game!\r\n"
TEXT_PLAYER_NUMBER = "*** You are player number %d (%d, %d)\r\n"
TEXT_PLAYER_JOINED_GAME = "*** %s has joined the game\r\n"
TEXT_PLAYER_LEFT_GAME = "*** %s has left the game\r\n"
TEXT_PLAYER_DISCONNECTED = "*** %s has disconnected\r\n"
TEXT_PLAYER_CHANGED_NICK = "*** %s changed nick to %s\r\n"
TEXT_PLAYER_STARTED_GAME = "*** %s has started the game\r\n"
TEXT_PLAYER_CREATED_GAME = "*** %s has created new game %s\r\n"
TEXT_PLAYER_PUSHED_TILE = "*** %s pushed the floating tile (%d, %d)\r\n"
TEXT_PLAYER_MOVED = "*** %s moved to (%d, %d)\r\n"
TEXT_PLAYER_ENDED_TURN = "*** %s ended the turn\r\n"
TEXT_PLAYER_TURN = "*** It's %s's turn (player number %d)\r\n"
TEXT_PLAYER_ROTATED_TILE = "*** You rotated the tile\r\n"
TEXT_PLAYER_TOOK_OBJECT = "*** %s picked up an object\r\n"
TEXT_TILE_ROTATED = "*** Floating tile rotated (%d)\r\n"
TEXT_CURRENT_GAMES = "*** Current games\n%s\r\n"
TEXT_DATA = "*** DATA %s\r\n"



class GameProtocol(LineReceiver):
    def connectionMade(self):
        self.nick = NICK_UNKNOWN_NAME
        self.game = None
        self.factory.connections.append(self)

    def connectionLost(self, reason):
        if self.nick != NICK_UNKNOWN_NAME:
            self.factory.notifyAllPlayers(TEXT_PLAYER_DISCONNECTED % self.nick)

        self.factory.connections.remove(self)

    def lineReceived(self, line):
        print line

        # TODO: keep track of how fast the commands are coming in in case
        #       someone is trying to spam the server

        args = line.split()

        if len(args) >= 1:
            if args[0] in self.factory.cmdDict.keys():
                cmdArgs = []
                if len(args) > 1:
                    cmdArgs = args[1:]

                self.transport.write(
                    self.factory.cmdDict[args[0]](self, *cmdArgs))
            else:
                self.transport.write(ERROR_UNKNOWN_COMMAND % args[0])


class GameFactory(Factory):
    protocol = GameProtocol

    def __init__(self):
        self.cmdDict = {
            '/list' : self.listGames,
            '/users' : self.listUsers,
            '/join' : self.joinGame,
            '/nick' : self.setNick,
            '/new' : self.newGame,
            '/start' : self.startGame,
            '/leave' : self.leaveGame,
            '/board' : self.printBoard,
            '/ft' : self.printFloatingTile,
            '/items' : self.printItemsRemaining,
            '/quit' : self.quit,
        }

        self.connections = []
        self.games = {}

    def listGames(self, proto, *args):
        buf = ''
        for gameKey in self.games.iterkeys():
            buf += "%s %d" % (gameKey, self.games[gameKey].playerCount)

        if not buf:
            buf = '  None'

        return TEXT_CURRENT_GAMES % buf

    def listUsers(self, proto, *args):
        pass

    def joinGame(self, proto, *args):
        if proto.nick == NICK_UNKNOWN_NAME:
            return ERROR_UNKNOWN_NICK_CREATE

        if not args:
            return ERROR_SPECIFY_GAME

        gameKey = args[0]

        if proto.game:
            return ERROR_GAME_JOINED

        if gameKey not in self.games.keys():
            return ERROR_UNKNOWN_GAME % gameKey

        if self.games[gameKey].started:
            return ERROR_GAME_STARTED

        if not self.games[gameKey].addPlayer(proto):
            return ERROR_JOIN_GAME
        else:
            proto.game = self.games[gameKey]

        return TEXT_JOIN_GAME % gameKey


    def setNick(self, proto, *args):
        if not args:
            return ERROR_SPECIFY_NICK
        elif len(args) > 1:
            return ERROR_SPACES_IN_NICK

        oldNick = proto.nick
        newNick = args[0]

        if len(newNick) < NICK_MIN_LENGTH:
            return ERROR_NICK_MIN_CHARS % NICK_MIN_LENGTH

        if len(newNick) > NICK_MAX_LENGTH:
            return ERROR_NICK_MAX_CHARS % NICK_MAX_LENGTH

        if newNick == NICK_UNKNOWN_NAME:
            return ERROR_NOT_PERMITTED

        for c in newNick:
            if c not in NICK_VALID_CHARS:
                return ERROR_NICK_CHARS

        if newNick == proto.nick:
            return ERROR_NICK_IS_SAME % newNick

        if self.lookupNick(newNick):
            return ERROR_NICK_EXISTS

        self.notifyAllPlayers(
            msg=TEXT_PLAYER_CHANGED_NICK % (oldNick, newNick),
            excludeProto=proto)

        proto.nick = newNick

        return TEXT_SET_NICK % newNick

    def newGame(self, proto, *args):
        if proto.nick == NICK_UNKNOWN_NAME:
            return ERROR_UNKNOWN_NICK_CREATE

        if proto.game:
            return ERROR_GAME_JOINED

        while True:
            newKey = createUniqueKey()

            if not newKey in self.games.keys():
                self.games[newKey] = NetworkGame(newKey)
                break

        self.notifyAllPlayers(
            msg=TEXT_PLAYER_CREATED_GAME % (proto.nick, newKey))

        return self.joinGame(proto, newKey)


    def startGame(self, proto, *args):
        pass

    def leaveGame(self, proto, *args):
        pass

    def printBoard(self, proto, *args):
        pass

    def printFloatingTile(self, proto, *args):
        pass

    def printItemsRemaining(self, proto, *args):
        pass

    def quit(self, proto, *args):
        # XXX - do something if the game has started
        if proto.game:
            self.games[proto.game.gameKey].players.remove(proto)

        proto.transport.loseConnection()

    def lookupNick(self, nick):
        for proto in self.connections:
            if proto.nick == nick:
                return proto
        return None

    def notifyAllPlayers(self, msg, excludeProto=None):
        for proto in self.connections:
            if proto == excludeProto:
                continue
            proto.transport.write(msg)

class NetworkGame:
    def __init__(self, gameKey):
        self.gameKey = gameKey
        self.players = [None, None, None, None]
        self.started = False
        self.board = board.Board()

    def getPlayerCount(self):
        count = 0

        for player in self.players:
            if player:
                count += 1

        return count

    playerCount = property(getPlayerCount, None)

    def addPlayer(self, proto):
        addedPlayer = False

        for count, player in enumerate(self.players):
            if not player:
                self.players[count] = proto
                addedPlayer = True
                break

        return addedPlayer

def createUniqueKey():
    return hashlib.new('md5',
        str(time.time()) + str(random.randint(0, 1000))).hexdigest()

def main():
    reactor.listenTCP(PORT, GameFactory())
    reactor.run()

if __name__ == '__main__':
    main()

