#
# server.py
# (c) 2009, 2010 pdevine@sonic.net
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

VALID_CHARS = string.ascii_letters + string.digits + ' '
NICK_LENGTH = 10

#
# Server specific error strings
#
# These are errors specific to the server.  Play errors are raised in the
# board.py module.
#
#

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

#
# Server event text strings
#
# These are text strings which can be returned by the server.  They can
# be used to trigger AI actions.
#

TEXT_SET_NICK = "*** You are now known as %s\n"
TEXT_JOIN_GAME = "*** You have joined game %s\n"
TEXT_YOUR_TURN = "*** It's your turn\n"
TEXT_YOU_WIN = "*** You won the game!\n"
TEXT_PLAYER_WON = "*** %s has won the game!\n"
TEXT_PLAYER_NUMBER = "*** You are player number %d (%d, %d)\n"
TEXT_PLAYER_JOINED_GAME = "*** %s has joined the game\n"
TEXT_PLAYER_LEFT_GAME = "*** %s has left the game\n"
TEXT_PLAYER_CHANGED_NICK = "*** %s changed nick to %s\n"
TEXT_PLAYER_STARTED_GAME = "*** %s has started the game\n"
TEXT_PLAYER_CREATED_GAME = "*** %s has created new game %s\n"
TEXT_PLAYER_PUSHED_TILE = "*** %s pushed the floating tile (%d, %d)\n"
TEXT_PLAYER_MOVED = "*** %s moved to (%d, %d)\n"
TEXT_PLAYER_ENDED_TURN = "*** %s ended the turn\n"
TEXT_PLAYER_TURN = "*** It's %s's turn (player number %d)\n"
TEXT_PLAYER_ROTATED_TILE = "*** You rotated the tile\n"
TEXT_PLAYER_TOOK_OBJECT = "*** %s picked up an object\n"
TEXT_TILE_ROTATED = "*** Floating tile rotated (%d)\n"
TEXT_CURRENT_GAMES = "*** Current games\n%s"
TEXT_DATA = "*** DATA %s"

gameBoards = {}
clientDict = {}

def listGames(client, *args):
    '''List current games which are being played on the server'''

    # XXX - Currently this displays the board UUID key and the number
    #       of players currently in the game
    #
    #       This needs to display:
    #          - players in the game
    #          - game started
    #          - last move time (?)
    #          - game duration

    buf = []
    for game in gameBoards.keys():
        buf.append('%s %d' % (game, gameBoards[game].playerCount))
    return TEXT_CURRENT_GAMES % '\n'.join(buf) + '\n'

def joinGame(client, *args):
    '''Join a game which has been created but not started'''

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

        notifyPlayers(client, TEXT_PLAYER_JOINED_GAME % client.name)

    return TEXT_JOIN_GAME % gameKey

def leaveGame(client, *args):
    '''Leave a game which has been joined'''

    if not client.game:
        return ERROR_JOIN_GAME

    notifyPlayers(client, TEXT_PLAYER_LEFT_GAME % client.name)

    # XXX - need to make a call out to the board to tell it that we're no
    #       longer joined -- this could result in the game being won

    client.game.players.remove(client)
    cleanupGame(client.game.gameKey)
    client.game = None

def cleanupGame(gameKey):
    '''Destroy a game board which has no more players left'''
    print "Cleanup games"
    game = clientDict.get(gameKey)

    if game:
        for player in game.players:
            if player:
                return

    del gameBoards[gameKey]

def setNick(client, *args):
    '''Set the nick name of player'''

    if not args:
        return ERROR_SPECIFY_NICK

    oldName = client.name
    newName = ' '.join(args)

    if len(newName) > NICK_LENGTH:
        return ERROR_NICK_MAX_CHARS % NICK_LENGTH

    for c in newName:
        if c not in VALID_CHARS:
            return ERROR_NICK_CHARS

    if lookupNick(newName):
        return ERROR_EXISTING_NICK

    client.name = newName
    notifyAllPlayers(TEXT_PLAYER_CHANGED_NICK % (oldName, client.name))

    return TEXT_SET_NICK % client.name
    
def lookupNick(nick):
    '''Find the client object associated with a particular nick'''
    for client in clientDict.keys():
        if clientDict[client].name == nick:
            return clientDict[client]
    return None

def startGame(client, *args):
    '''Start a game that has been joined'''
    # XXX - only allow starting by the person who created the game?

    if not client.game:
        return ERROR_JOIN_GAME

    if hasattr(client.game.board, 'board'):
        return ERROR_GAME_STARTED

    try:
        client.game.board.createBoard(client.game.playerCount)
    except board.BoardCreationError, msg:
        return ERROR_NEED_PLAYERS

    notifyPlayers(client, TEXT_PLAYER_STARTED_GAME % client.name)

    for count, player in enumerate(client.game.players):
        if player:
            location = client.game.board.players[count].location
            notifyPlayer(client,
                         count+1,
                         TEXT_PLAYER_NUMBER % (count+1,
                                               location[0],
                                               location[1]))

    # the player who starts the game isn't always the player whose turn
    # it is first
    notifyPlayer(client, client.game.board.playerTurn, TEXT_YOUR_TURN)


def newGame(client, *args):
    '''Create a new game'''
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

    notifyAllPlayers(TEXT_PLAYER_CREATED_GAME % (client.name, gameKey))

    joinGame(client, gameKey)

def printBoard(client, *args):
    '''Print an ascii representation of the game board'''

    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    asciiBoard = client.game.board.asciiBoard()
    rows = []
    for count, row in enumerate(asciiBoard.split('\n')):
        if row:
            if count > 0:
                rows.append("    " + row)
            else:
                rows.append(row)

    return '\n'.join(rows) + '\n'

def printFloatingTile(client, *args):
    '''Print an ascii representation of the floating tile'''
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    ft = client.game.board.floatingTile.asciiTile()
    rows = []
    for count, row in enumerate(ft.split('\n')):
        if row:
            if count > 0:
                rows.append("    " + row)
            else:
                rows.append(row)
    return '\n'.join(rows) + '\n'

def printItemsRemaining(client, *args):
    '''Print remaining items for the player'''
    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    # XXX - add a check for the game type here?

    player = client.game.board.players[client.getPlayerNumber()-1]
    return player.getAsciiItemsRemaining() + '\n'

def printHelp(client, *args):
    return 'XXX - Not Implemented\n'

def listUsers(client, *args):
    '''Print a list of all users on the server'''

    buf = []
    for userKey in clientDict.keys():
        user = clientDict[userKey]
        if user.game:
            buf.append('%s : %s' % (user.name, user.game.gameKey))
        else:
            buf.append('%s : No Game' % user.name)

    return '\n'.join(buf) + '\n'

def rotateFloatingTile(client, *args):
    '''Rotate the floating tile clockwise or anti-clockwise'''

    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    if len(args) != 1:
        return ERROR_ROTATE_DIRECTION

    try:
        if args[0].lower() in ['1', 'clockwise', 'clock']:
            client.game.board.rotateClockwise(client.getPlayerNumber())
            notifyPlayers(client, TEXT_TILE_ROTATED % 1)
        elif args[0].lower() in ['2', 'counterclockwise', 'counter']:
            client.game.board.rotateCounterClockwise(client.getPlayerNumber())
            notifyPlayers(client, TEXT_TILE_ROTATED % 2)
    except (board.BoardMovementError, board.GameOverError), msg:
        return "ERROR: %s\n" % str(msg)

    return TEXT_PLAYER_ROTATED_TILE


def printSerializedBoard(client, *args):
    '''Dump the current game state in a machine parseable way'''

    if not client.game:
        return ERROR_JOIN_GAME

    if not hasattr(client.game.board, 'board'):
        return ERROR_START_GAME

    return TEXT_DATA % client.game.board.serialize()

def moveRow(client, *args):
    '''Push the floating tile onto a row on the board'''

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
    except (board.BoardMovementError, board.GameOverError), msg:
        return "ERROR: %s\n" % str(msg)

    notifyPlayers(client, TEXT_PLAYER_PUSHED_TILE % (client.name, row, dir))


def moveColumn(client, *args):
    '''Push the floating tile onto a column on the board'''

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
    except(board.BoardMovementError, board.GameOverError), msg:
        return "ERROR: %s\n" % str(msg)

    notifyPlayers(client, TEXT_PLAYER_PUSHED_TILE % (client.name, col, dir))


def movePlayer(client, *args):
    '''Move a player to a location on the board'''

    if len(args) != 2:
        return ERROR_COLUMN_ROW

    try:
        col = int(args[0])
        row = int(args[1])
    except ValueError:
        return ERROR_COLUMN_ROW

    try:
        client.game.board.movePlayer(client.getPlayerNumber(), col, row)
    except (board.PlayerMovementError, board.GameOverError), msg:
        return "ERROR: %s\n" % str(msg)

    notifyPlayers(client, TEXT_PLAYER_MOVED % (client.name, col, row))


def endTurn(client, *args):
    '''End the turn'''

    # XXX - notify if a board item was picked up

    itemFound = False

    try:
        itemFound = client.game.board.endTurn(client.getPlayerNumber())
    except board.PlayerTurnError, msg:
        return "ERROR: %s\n" % str(msg)

    if itemFound:
        notifyPlayers(client, TEXT_PLAYER_TOOK_OBJECT % (client.name))

    if client.game.board.gameOver:
        notifyPlayers(client, TEXT_PLAYER_WON % client.name)
        return TEXT_YOU_WIN
    else:
        notifyPlayers(client, TEXT_PLAYER_ENDED_TURN % client.name)
        notifyPlayers(client, TEXT_PLAYER_TURN % (client.name,
                                                  client.game.board.playerTurn))
        notifyPlayer(client, client.game.board.playerTurn, TEXT_YOUR_TURN)

    return ''

def notifyPlayers(client, msg):
    '''Send a message to all players in the game'''

    for player in client.game.players:
        if player:
            player.send(msg)

def notifyPlayer(client, player, msg):
    '''Send a message to an individual player'''
    client.game.players[player-1].send(msg)

def notifyAllPlayers(msg):
    '''Send a message to all players on the server'''

    for client in clientDict.keys():
        clientDict[client].send(msg)

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
        try:
            self.client.send('%04d' % len(msg) + msg)
        except:
            print "client not listening: %s" % msg
            pass


#
# Handy debug method for trouble shooting any errors.  This dumps the
# server into the python debugger and prints the stack traceback
#

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
    '/board' : printBoard,
    '/ft' : printFloatingTile,
    '/items' : printItemsRemaining,
    '/data' : printSerializedBoard,
    '/pushrow' : moveRow,
    '/pushcolumn' : moveColumn,
    '/move' : movePlayer,
    '/end' : endTurn,
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
                try:
                    data = sock.recv(size)
                except:
                    input.remove(sock)
                    del clientDict[sock]
                    continue
                if data:
                    # all commands start with /
                    if data.startswith('/'):
                        cmds = data.split('\n')
                        print cmds
                        for cmdLine in cmds:
                            tokens = cmdLine.split()
                            print tokens
                            if not tokens:
                                continue
                            cmd = commandDict.get(tokens[0])
                            if cmd:
                                buf = cmd(clientDict[sock], *tokens[1:])
                                if buf:
                                    try:
                                        sock.send('%04d' % len(buf) + buf)
                                    except:
                                        buf = "%s left\n" % \
                                            clientDict[sock].name
                                        input.remove(sock)
                                        del clientDict[sock]
                            else:
                                buf = ERROR_UNKNOWN_COMMAND % tokens[0]
                                try:
                                    sock.send('%04d' % len(buf) + buf)
                                except:
                                    buf = "%s left\n" % clientDict[sock].name
                                    input.remove(sock)
                                    del clientDict[sock]
                else:
                    buf = "%s left\n" % clientDict[sock].name
                    if clientDict[sock].game:
                        clientDict[sock].game.players.remove(clientDict[sock])
                        cleanupGame(clientDict[sock].game.gameKey)
                        clientDict[sock].game = None
                    sock.close()
                    input.remove(sock)
                    del clientDict[sock]
                    print buf.rstrip()

    server.close()

if __name__ == '__main__':
    main()

