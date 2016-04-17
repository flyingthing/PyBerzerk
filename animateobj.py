import pygame
from config import *

class AnimateObj(pygame.sprite.Sprite):
    def __init__(self, callback=None):
        super(AnimateObj, self).__init__()
        self.index = 0
        self.image = None
        self.images = []
        self.patterndictionary = {}
        self.pattern = []
        self.rect = None
        self.cbAnimate = callback
        self.color = None
        self.patternkey = None

    def addpattern(self, name, array):
        self.patterndictionary.update({name: array})

    def setpattern(self, pattern):
        self.pattern = self.patterndictionary[pattern]
        if self.image is None:
            self.image = self.images[self.pattern[0]]
        self.patternkey = pattern

    def update(self):
        self.index += 1
        if self.index >= len(self.pattern):
            if self.cbAnimate is not None:
                self.cbAnimate(self)
            self.index = 0
        self.image = self.images[self.pattern[self.index]]

    def draw(self):
        pass

    def setcolor(self, color):
        self.color = color
        for image in self.images:
            pixelArray = pygame.PixelArray(image)
            pixelArray.replace(WHITE, color)

    def moveposition(self, x, y):
        self.rect.x += x
        self.rect.y += y
