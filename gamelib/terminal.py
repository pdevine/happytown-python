import sys
import xmlrpclib
import socket

SERVER_URL = None
PROXY = None
GAMEKEY = ''

PROGINFO = """Truva Network CLI v1.0\n(c) 2009 Patrick Devine\n\n"""

GAME_LIST_HEADER = "# Players Started\n-----------------------------"
GAME_LIST_FORMAT = "%d %s       %s %s"

def createServerUrl(server='localhost', port=8000):
    return 'http://%s:%s' % (server, port)

def getNetworkInfo(server='localhost', port=8000):
    while True:
        serverString = raw_input("Network Server [%s]: " % server)
        if serverString == '':
            break
        else:
            # XXX - should probably do some validation here
            server = serverString.strip()
            break

    while True:
        portString = raw_input("Network Port [%d]: " % (port))
        if portString == '':
            break
        else:
            try:
                port = int(portString.strip())
            except:
                pass
            else:
                break

    print "\nNetwork Server: %s" % server
    print "Port          : %d" % port

    return (server, port)

def main():
    global PROXY, GAMEKEY

    promptNewGame = False
    gameCache = []

    print PROGINFO
    networkProxyInfo = getNetworkInfo()

    try:
        print "Contacting Game Server"
        PROXY = xmlrpclib.ServerProxy(createServerUrl(*networkProxyInfo))
        gameList = PROXY.listGames()
        gameList = gameList.rstrip()
    except socket.error:
        print "Couldn't contact game server..."
        sys.exit(1)

    if not gameList:
        print "No games currently started"
        promptNewGame = True
    else:
        print GAME_LIST_HEADER
        for count, game in enumerate(gameList.split('\n')):
            (gameDate, gameTime, currentPlayers, gameKey) = game.split()

            # save the gamekeys to start a new game
            gameCache.append(gameKey)

            print GAME_LIST_FORMAT % \
                (count+1, currentPlayers, gameTime, gameDate)

        while True:
            gamePrompt = \
                raw_input("Select game, 'n'ew, 'q'uit: (1-%d,n,q): " % (count+1))
            if gamePrompt.lower() == 'n':
                promptNewGame = True
                break
            elif gamePrompt.lower() == 'q':
                sys.exit(0)

            try:
                gameNumber = int(gamePrompt)
            except:
                pass
            else:
                if gameNumber > 0 and gameNumber <= count+1:
                    break

    while promptNewGame:
        newGame = raw_input("Start new game? (y/n): ")
        if newGame.lower() == 'n':
            sys.exit(0)
        elif newGame.lower() == 'y':
            GAMEKEY = PROXY.newGame()
            break



if __name__ == '__main__':
    main()


