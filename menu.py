import pygame
import util

from options import *

class Menu:
    menuOptions = ("New Game", "Quit")

    def __init__(self, screen):
        self.screen = screen

        self.logo = util.loadImage("title.png")
        self.font = util.loadFont("Cosmetica.ttf", 28)

        self.bg = pygame.Surface(screen.get_size())
        self.bg = self.bg.convert()
        self.bg.fill((52, 56, 91))

        self.menuSelect = 0

    def run(self):
        done = False

        while not done:
            self.screen.blit(self.bg, self.screen.get_rect())

            boxColor = (250, 250, 250)
            boxRectangle = (20, self.logo.get_height()-20, 
                SCREEN_WIDTH-40, SCREEN_HEIGHT-self.logo.get_height())
            pygame.draw.rect(self.bg, boxColor, boxRectangle, 2)
            for option in range(len(self.menuOptions)):
                self.render(self.menuOptions[option], option)

            rect = self.logo.get_rect()
            rect.centerx = self.screen.get_rect().centerx
            rect.top = 0
            self.screen.blit(self.logo, rect)

            pygame.display.flip()
            nextFrame = False
            while not nextFrame:
                pygame.event.post(pygame.event.wait())
                for event in pygame.event.get():
                    if event.type == NEXTFRAME:
                        nextFrame = True
                    elif event.type == KEYDOWN:
                        if event.key == K_UP:
                            self.menuSelect -= 1
                            if self.menuSelect < 0:
                                self.menuSelect = len(self.menuOptions) - 1
                        elif event.key == K_DOWN:
                            self.menuSelect += 1
                            if self.menuSelect >= len(self.menuOptions):
                                self.menuSelect = 0
                        elif event.key == K_SPACE or event.key == K_RETURN:
                            done = True

        return self.menuSelect


    def render(self, text, menuId):
        if self.menuSelect == menuId:
            color = (220, 120, 20)
        else:
            color = (250, 250, 250)

        image = self.font.render(text, True, color)

        rect = image.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.top = self.logo.get_height() + 100 + menuId * rect.height * 1.1

        self.screen.blit(image, rect)

