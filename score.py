import pygame, spritesheet
from itertools import cycle
from config import *

class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = pygame.font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
        pass

class Score(pygame.sprite.Sprite):
    score = 0
    bonuslife = True

    @staticmethod
    def addpoints(points):
        Score.score += points
        if Score.score >= BONUS_LIFE_SCORE and Score.bonuslife:
            event = pygame.event.Event(BONUS_LIFE)
            pygame.event.post(event)
            Score.bonuslife = False

    def __init__(self,color):
        super(Score,self).__init__()
        self.scorecolor = color

    def update(self):
        tmp = '{:>7}'.format(Score.score)

        # FIX THIS SHOULD BE BASED ON FONT SIZE
        text = Text(FONT, 20, tmp, self.scorecolor, 60, SCREEN_HEIGHT - BORDERTHICKNESS - WALLTHICKNESS )
        self.image = text.surface
        self.rect = text.rect

    def draw(self):
        pass

class Bonus(pygame.sprite.Sprite):
    def __init__(self, color, bonus):
        super(Bonus,self).__init__()
        Score.addpoints(bonus)
        bonus = 'BONUS  {:3d}'.format(bonus)
        text = Text(FONT, 20, bonus, color, (SCREEN_WIDTH/5)*2, SCREEN_HEIGHT - BORDERTHICKNESS - WALLTHICKNESS)
        self.image = text.surface
        self.rect = text.rect

    def update(self):
        pass

    def draw(self):
        pass


class gameFPS(pygame.sprite.Sprite):
    clock = 0
    color = BLACK
    displayIterator = cycle(range(2))
    display = displayIterator.next()

    @staticmethod
    def toggleDisplay():
        gameFPS.display = gameFPS.displayIterator.next()

    def __init__(self,color=BLACK):
        super(gameFPS,self).__init__()
        gameFPS.color = color

    def update(self):
        color = BLACK
        if gameFPS.display == True:
            color = gameFPS.color
        fps = "FPS: {:.2f}".format(gameFPS.clock)
        text = Text(FONT,12,fps,color,SCREEN_WIDTH - 90, SCREEN_HEIGHT - BORDERTHICKNESS)
        self.image = text.surface
        self.rect = text.rect

    def draw(self):
        pass


