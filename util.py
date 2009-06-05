import os.path
import pygame

from pygame.locals import *

def loadImage(fileName):
    try:
        imageName = os.path.join("data", fileName)
        image = pygame.image.load(imageName).convert_alpha()
    except pygame.error, message:
        print "Couldn't load image %s" % (fileName)
        raise
    image = image.convert()
    colorKey = image.get_at((0,0))
    image.set_colorkey(colorKey, RLEACCEL)

    return image
        
def loadFont(fontName, size):
    try:
        font = pygame.font.Font(os.path.join("data", fontName), size)        
    except pygame.error, message:
        print "Couldn't load font %s" % (fontName)
        raise
    return font

def locationString(column, row):
    return "%d:%d" % (column, row)
