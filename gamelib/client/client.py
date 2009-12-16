import sys
import pyglet
import random

sys.path.append('../')
import events

import menu
import character
import client_board
import client_network

from pyglet.window import key

import xmlrpclib

window = pyglet.window.Window(1024, 768)
#window = pyglet.window.Window(fullscreen=True)

pyglet.font.add_file('../../data/depraved.ttf')
pyglet.font.add_file('../../data/jamaistevie.ttf')

class Title(object):
    def __init__(self):
        self.label_front = \
            pyglet.text.Label('Truva',
                              font_name='Depraved',
                              font_size=120,
                              color=(255, 50, 0, 255),
                              x=512,
                              y=670,
                              anchor_x='center', 
                              anchor_y='center')

        self.label_back = \
            pyglet.text.Label('Truva',
                              font_name='Depraved',
                              font_size=120,
                              color=(255, 255, 255, 255),
                              x=502,
                              y=670,
                              anchor_x='center', 
                              anchor_y='center')

        pyglet.clock.schedule(self.update)

        self.timer = 2

        self.positions = (670, 665)

    def update(self, dt):
        self.timer -= dt

        if self.timer <= 0:
            if self.label_front.y == self.positions[0]:
                self.label_front.y = self.positions[1]
                self.label_back.y = self.positions[1] - 10
            else:
                self.label_front.y = self.positions[0]
                self.label_back.y = self.positions[0] - 10

            if self.timer <= -0.5:
                self.timer = random.randint(1, 5)

    def draw(self):
        self.label_back.draw()
        self.label_front.draw()


class NetworkGame(object):
    def __init__(self, serverUrl='http://localhost:8000'):
        gameServer = xmlrpclib.ServerProxy(serverUrl)

        self.serverResponding = True

        try:
            self.gameList = gameServer.listGames()
        except socket.error:
            self.serverResponding = False
            self.gameList = []

pyglet.clock.schedule(events.consumeEvents)

#title = Title()
gameBoard = client_board.Board(demo=True)
gameBoard.pourIn()
#menu = menu.NewGameMenu()
person = character.Character()
networkClient = client_network.ClientHandler()
networkClient.joinFirstGame()

@window.event
def on_draw():
    window.clear()
    gameBoard.draw()
    #title.draw()
    #menu.draw()
    #person.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    #menu.mousePress(x, y, button, modifiers)
    pass

@window.event
def on_mouse_release(x, y, button, modifiers):
    #menu.mouseRelease(x, y, button, modifiers)
    pass

@window.event
def on_mouse_motion(x, y, dx, dy):
    #menu.mouseMotion(x, y, dx, dy)
    pass

@window.event
def on_key_release(symbol, modifiers):
    #menu.keyRelease(symbol, modifiers)
    pass

@window.event
def on_key_press(symbol, modifiers):
    #menu.keyPress(symbol, modifiers)
    #person.keyPress(symbol, modifiers)
    pass

pyglet.app.run()

