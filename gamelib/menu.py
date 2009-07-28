import pygame
import util

from options import *

class Title(object):
    def __init__(self, bg):
        self.bg = bg
        titleFont = util.loadFont("depraved.ttf", 160)

        self.image = titleFont.render('Truva', True, (0, 0, 0))
        self.rect = self.image.get_rect()

        self.rect.centerx = self.bg.get_rect().centerx
        self.rect.top = 40

        self.horiz = 1
        self.vert = 1

    def update(self, tick):
        self.rect.x += self.horiz
        self.rect.y += self.vert

        if self.horiz > 0 and self.rect.x >= 140 or \
           self.horiz < 0 and self.rect.x <= 100:
            self.horiz = -self.horiz

        if self.vert > 0 and self.rect.y >= 58 or \
           self.vert < 0 and self.rect.y <= 30:
            self.vert = -self.vert

    def draw(self):
        self.bg.blit(self.image, self.rect)

class Menu:
    menuOptions = ("New Game", "Quit")

    def __init__(self, screen):
        self.screen = screen

        self.done = False
        #self.font = util.loadFont("Base 02.ttf", 58)
        self.font = util.loadFont("PlAGuEdEaTH_0.ttf", 68)

        #self.bg = pygame.Surface(screen.get_size())
        #self.bg = self.bg.convert()
        #self.bg.fill((52, 56, 91))

        self.menuSelect = 0

        self.title = Title(self.screen)

        self.clock = pygame.time.Clock()

    def run(self):
        while True:

            self.handleEvents()
            if self.done:
                break

            tick = self.clock.tick(30)

            self.title.update(tick)
            self.screen.fill((52, 56, 91))

            #self.screen.blit(self.bg, self.screen.get_rect())

            self.title.draw()

            for option in range(len(self.menuOptions)):
                self.draw(self.menuOptions[option], option)

            pygame.display.flip()

        return self.menuSelect


    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.menuSelect -= 1
                    if self.menuSelect < 0:
                        self.menuSelect = len(self.menuOptions) - 1
                elif event.key == K_DOWN:
                    self.menuSelect += 1
                    if self.menuSelect >= len(self.menuOptions):
                        self.menuSelect = 0
                elif event.key == K_SPACE or event.key == K_RETURN:
                    self.done = True


    def draw(self, text, menuId):
        if self.menuSelect == menuId:
            color = (220, 120, 20)
        else:
            color = (250, 250, 250)

        image = self.font.render(text, True, color)

        rect = image.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.top = 200 + menuId * rect.height * 1.1

        self.screen.blit(image, rect)

