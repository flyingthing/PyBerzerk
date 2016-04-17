import pygame, spritesheet, random
from config import *
from animateobj import *
import player
import cmath

import time
import math

class Otto(AnimateObj):
    def __init__(self, color, player, filename, rect, count, colorkey=BLACK, scale=2):
        super(Otto ,self).__init__(self.ottocb)
        ss = spritesheet.spritesheet(filename)
        self.images =  ss.load_strip(rect, count, colorkey)
        self.frame = 15
        self.moveTime = 400
        self.timer = pygame.time.get_ticks()

        self.setcolor(color)

        for i in range(count):
            image = self.images[i]
            w,h = image.get_size()
            cropped_image = image.subsurface(0, 0, w, h)
            scale_image = pygame.transform.scale(cropped_image,(scale*w, scale*h))
            self.images[i] = scale_image

        self.rect = self.images[0].get_rect()

        # otto starts at player start position
        self.rect.x = player.start_x
        self.rect.y = player.start_y


        self.addpattern("spawn",[0,1,3,4])
        self.addpattern("otto", [4])
        self.setpattern("spawn")

        self.player = player

        self.step = 0
        self.dir = 2
        self.y = self.rect.y

    def ottocb(self, *args):
        self.setpattern("otto")
        self.callback = None

    def update(self):
        self.frame -= 1
        if self.frame == 0:
            self.frame = 5
            #if currentTime - self.timer > self.moveTime:
            super(Otto, self).update()

            if self.patternkey == "otto":
                player = complex(self.player.rect.centerx, self.player.rect.centery)
                otto = complex(self.rect.centerx, self.rect.centery)
                cc = player - otto

                sign = lambda x: (x > 0) - (x < 0)

                #deltaX = sign(int(cc.real))
                #deltaX *= 3
                self.rect.x += 3*sign(int(cc.real))
                #deltaY = sign(int(cc.imag))
                #deltaY *= 3
                self.y += 3*sign(int(cc.imag))

        self.bounce()
        self.rect.y = self.y + self.step

    def draw(self, *args):
        pass

    def voffset(self):
        offset = 0
        pass

    #
    def bounce(self):
        AMPLITUDE = 50
        self.step += self.dir
        if self.step >= AMPLITUDE:
            self.dir *= -1
            self.step += self.dir
        if self.step <= 0:
            self.dir *= -1
            self.step += self.dir