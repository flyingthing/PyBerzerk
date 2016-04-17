import sys
import pygame
from config import *

class WallObject(pygame.sprite.Sprite):
    def __init__(self, screen, color, rect):
        super(WallObject,self).__init__()
        self.screen = screen
        self.color = color
        self.rect = rect.copy()
        self.wallthickness = WALLTHICKNESS

        # create an image of the block and fill it with color
        self.image = pygame.Surface([rect.width,rect.height])
        self.image.fill(color)

    def draw(self):
        pass
