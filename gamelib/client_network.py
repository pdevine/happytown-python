
import re
import network
import server

class ClientHandler(network.ClientBaseHandler):
    def __init__(self):
        network.ClientBaseHandler.__init__(self)

    def joinFirstGame(self):
        self.send('/list')

        games = self.receive()

        # XXX - this will need to change if the /list command
        #       changes what it returns

        games = games.strip()
        print "[" + games + "]"

        if games:
            game = games.split('\n')[0]
            gameKey, totalPlayers = game.split()
            self.joinGame(gameKey)
        else:
            self.send('/new')

            createGameText = server.TEXT_PLAYER_CREATED_GAME % \
                (self.nick, "(\w+)")
            createGameText = re.sub('\*', '\*', createGameText)

            gameKey = ''

            while True:
                msg = self.receive()

                print "text = [" + createGameText + "]"
                print "msg = [" + msg + "]"

                mObj = re.match(createGameText, msg)
                if mObj:
                    gameKey = mObj.groups()[0]
                    break


