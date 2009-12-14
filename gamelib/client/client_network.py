
import re
import network
import server

import pyglet

class ClientHandler(network.ClientBaseHandler):
    def __init__(self):
        network.ClientBaseHandler.__init__(self)

#        pyglet.clock.schedule(self.update)
#
#    def update(self, tick):
#        self.receive()

    def joinFirstGame(self):
        self.send('/list')

        games = self.receive(retry=True)

        # XXX - this will need to change if the /list command
        #       changes what it returns

        if not games:
            print "No games found"
            return

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


