#!/usr/bin/python

import pygame

from menu import Menu
from game import Game
from pygame.locals import  *

from options import *

import tile

def init():
    pass
#    tile.init()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("The Labyrinth")

    init()

    pygame.time.set_timer(NEXTFRAME, 1000 / FPS)

    while True:
        selection = Menu(screen).run()
        if selection == 0:
            Game(screen).run()
        else:
            return

if __name__ == "__main__":
    main()


