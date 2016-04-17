import sys
import pygame
from pygame.locals import *
from config import *
from operator import itemgetter
import pickle

def gameOver(screen, score):
    bRet = False
    hs = getHighScores()
    if 0 <= hs.__len__() < 10:
        if score > 0:
            hallOfFame(screen, hs, score)
            bRet = True
        else:
          _gameOver(screen)
    else:
        for (name,topscore) in hs:
            if score > topscore:
                hallOfFame(screen, hs, score)
                bRet = True
                break
        else:
            _gameOver(screen)
    return bRet

def _gameOver(screen):
    _gameWait(screen, "GAME OVER", "Press SPACEBAR to Start", K_SPACE)

def gamePause(screen):
    _gameWait(screen, "GAME PAUSE", "Press F1 To Continue", K_F1)

def _gameWait(screen, msg, submsg, key):
    font_path = FONT_PATH
    font_size = 32
    fontObj = pygame.font.Font(font_path, font_size)
    txt = fontObj.render(msg, 1, GREEN)
    width = txt.get_width()
    height = txt.get_height()
    screen.blit(txt, (MAZE_CENTERX - width/2, MAZE_CENTERY - height/2))

    font_size = 10
    fontObj = pygame.font.Font(font_path, font_size)
    txt = fontObj.render(submsg, 1, GREEN)
    width = txt.get_width()
    h = height
    height = txt.get_height()
    screen.blit(txt, (MAZE_CENTERX - width/2, MAZE_CENTERY + h - height/2))

    pygame.display.flip()
    wait4User(screen, key )

def wait4User(screen, key):
    pause = True
    while pause:
        for e in pygame.event.get():
            keys = pygame.key.get_pressed()
            if e.type == QUIT or keys[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if keys[key]:
                pause = False
                break
    pygame.event.clear((KEYUP,KEYDOWN))
    pygame.key.get_pressed()
    pygame.event.get()
    screen.fill(BLACK)
    pygame.display.flip()


# clear maze screen area
def screenMazeClear(screen):
    screen.fill(BLACK)
    pygame.display.flip()
    screen.fill(BLACK)
    pygame.display.flip()

# NOTE: scroll opposite direction players exits, i.e. exit E, scroll W
def screenScroll(screen, exit, color):
    # amount to shift image for scroll
    dx, dy, iterations = {"N":(0,10,SCREEN_HEIGHT/10), "S":(0,-10, SCREEN_HEIGHT/10), "W":(10,0,SCREEN_WIDTH/10), "E":(-10,0,SCREEN_WIDTH/10)}[exit]

    # screen shot
    bg = screen.subsurface(0,0,SCREEN_WIDTH, BORDERTHICKNESS + MAZE_HEIGHT + WALLTHICKNESS*4).convert()

    # turn everything in maze BLUE
    pixelArray = pygame.PixelArray(bg)
    pixelArray.replace(color,WALL_COLOR)
    pixelArray.replace(GREEN,WALL_COLOR)
    del pixelArray

    for i in range(iterations):
        screen.blit(bg,(0,0))
        pygame.display.flip()
        pygame.time.delay(40)
        bg.scroll(dx,dy)

    screenMazeClear(screen)

def gameCntrls(screen):
    blinkMsg(screen, blinkCntrls, "Press Any Key To Exit")

def blinkCntrls(screen, msg, display=True):
    title = "PYGAME  BERZERK  CONTROLS"
    font_path = FONT_PATH
    font_size = 24
    font = pygame.font.Font(FONT,font_size)
    screen.fill(BLACK)
    fonttxt = font.render(title,1,GREEN)
    w,h = font.size(title)
    screen.blit(fonttxt,(SCREEN_WIDTH/2 - w/2, BORDERTHICKNESS))

    cntrls = ("[ LEFT ARROW KEY ] - Move the player left",
              "[ RIGHT ARROW KEY ] - Move the player right",
              "[ UP ARROW KEY ] -  Move the player up",
              "[ DOWN ARROW KEY ] - Move the player down",
              "[ SPACEBAR KEY ] - Fire laser",
              "[ F1 KEY ] - Pause game",
              "[ F2 KEY ] - Toggle frames-per-second display",
              "[ ESC KEY ] - Quit game"
              )

    font = pygame.font.Font(FONT, 16)
    y = BORDERTHICKNESS + h*3
    for txt in cntrls:
        fonttxt = font.render(txt,True,WHITE,BLACK)
        w,h = font.size(txt)
        screen.blit(fonttxt,(SCREEN_WIDTH/2 - w/2,y - h))
        y += h + h/2

    if display == True:
        font_size = 12
        font = pygame.font.Font(font_path,font_size)
        txt = font.render(msg,1,GREEN)
        txt_width = txt.get_width()
        txt_height = txt.get_height()
        screen.blit(txt,(SCREEN_WIDTH/2 - txt_width/2,SCREEN_HEIGHT - txt_height))

    pygame.display.flip()

def blinkMsg(screen, function, msg):
    pause = True
    keys = None
    display = True
    screen.fill(BLACK)
    pygame.display.flip()
    pygame.time.set_timer(BLINK,500)    # 0.5 sec event
    while pause:
        function(screen, msg, display)
        for e in pygame.event.get():
            if e.type == BLINK:
                display = not display
            keys = pygame.key.get_pressed()
            if e.type == QUIT or keys[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                pygame.time.set_timer(BLINK,0)
                pause = False
                break
    pygame.event.clear((KEYUP,KEYDOWN))
    pygame.key.get_pressed()
    pygame.event.get()
    screen.fill(BLACK)
    pygame.display.flip()
    return keys

def highScoresScreen(screen):
    return blinkMsg(screen, blinkHighScores, MSG1)

HIGH_SCORE = "High  Scores"
COPYRIGHT = u"\u00A9" + " 1980  STERN  Electronics,  Inc."
MSG1 = "How To Play: F1    Start Game: SPACEBAR"

def blinkHighScores(screen, msg, display):
    font_size = 24
    font = pygame.font.Font(FONT,font_size)
    screen.fill(BLACK)
    txt = font.render(HIGH_SCORE,1,GREEN)
    w,h = font.size(HIGH_SCORE)
    screen.blit(txt,(SCREEN_WIDTH/2 - w/2,BORDERTHICKNESS))
    pygame.draw.line(screen,WHITE,(SCREEN_WIDTH/5,BORDERTHICKNESS+30),(SCREEN_WIDTH/5*4, BORDERTHICKNESS+30), 4)

    hs = getHighScores()

    # determine x,y starting offset for high scores
    images = []
    txt = '10W00000WWXXX'     # template for highscore
    _colortext(txt,font,False,(BLACK),images)
    imglen = 0
    for img in images:
        imglen += img[0][0]
    y_offset = img[0][1]

    for i, (name,score) in enumerate(hs,1):
        x = SCREEN_WIDTH/2 - imglen/2
        images[:] = []  # clear the list

        # order highest score to lowest
        txt = '{:02d}W'.format(i)
        _colornum(txt,font,True,(RED),images)

        # score
        txt = '{:05d}W'.format(score)
        _colornum(txt,font,True,(YELLOW),images)

        # initials
        txt = '{:3}'.format(name)
        _colortext(txt,font,True,(DARK_ORCHID),images)

        y = BORDERTHICKNESS+30 + y_offset*i
        for img in images:
            x1,y1 = img[0]
            screen.blit(img[1],(x,y))
            x += x1

    txt = font.render(COPYRIGHT,True,WHITE,BLACK)
    w,h = font.size(COPYRIGHT)
    screen.blit(txt,(SCREEN_WIDTH/2 - w/2,SCREEN_HEIGHT - BORDERTHICKNESS*2 - h))
    pygame.draw.line(screen,WHITE,(SCREEN_WIDTH/5,SCREEN_HEIGHT - BORDERTHICKNESS*2 - h/2*3), (SCREEN_WIDTH/5*4, SCREEN_HEIGHT - BORDERTHICKNESS*2 - h/2*3), 4)
    pygame.draw.line(screen,WHITE,(SCREEN_WIDTH/5,SCREEN_HEIGHT - BORDERTHICKNESS*2 + h/2),   (SCREEN_WIDTH/5*4, SCREEN_HEIGHT - BORDERTHICKNESS*2 + h/2),   4)

    if display == True:
        font_size = 12
        font = pygame.font.Font(FONT_PATH,font_size)
        txt = font.render(MSG1,1,GREEN)
        txt_width = txt.get_width()
        txt_height = txt.get_height()
        screen.blit(txt,(SCREEN_WIDTH/2 - txt_width/2,SCREEN_HEIGHT - txt_height))

    pygame.display.flip()

def _colornum(text, font, flag, color, images):
    for c in text[:]:
        _color = color
        if (flag == True) and (c == '0'):
            _color = BLACK
        else:
            flag = False    # hiding leading zero character
        if c == 'W':
            _color = BLACK
        offset = font.size(c)
        img = font.render(c, True, _color, BLACK)
        images.append((offset,img))

def _colortext(text, font, flag, color, images):
    for c in text[:]:
        _color = color
        if flag == True:
            if c == ' ':
                c = 'W'
                _color = BLACK
        offset = font.size(c)
        img = font.render(c, True, _color, BLACK)
        images.append((offset,img))


def getHighScores():
    highscores = []

    #test if file exists
    try:
        with open('highscores.txt', 'r') as file:
            highscores = pickle.load(file)
            high_scores = sorted(highscores, key=itemgetter(1), reverse=True)[:10]
    except IOError as e:
        # doesn't exists
        pass

    return highscores

def hallOfFame(screen, highscores, score):
    font_path = FONT_PATH
    font_size = 24
    font = pygame.font.Font(FONT,font_size)
    screen.fill(BLACK)

    tbl = [((YELLOW),1, "Congratulations  Player"),
           ((BLACK), 1, " "),
           ((DEEPSKYBLUE), 1, "You have joined the immortals"),
           ((DEEPSKYBLUE), 1, "in the BERZERK hall of fame"),
           ((BLACK), 1, " "),
           ((DEEPSKYBLUE), 1.5, "Enter you initials:"),
           ((WHITE), 1, "W|W|W"),
           ((WHITE), 1, " "),
           ((GREEN), 1, "Move Up/Down Arrow-Keys to change letter"),
           ((GREEN), 1, "then press Right Arrow-Key to store it.")]

    y = BORDERTHICKNESS*3
    coor = None
    for (color, factor, txt) in tbl:
        fonttxt = font.render(txt,True,color,BLACK)
        w,h = font.size(txt)
        if txt == "W|W|W":
            coor = getInitialCoor(font,SCREEN_WIDTH/2 - w/2,y)
        else:
            screen.blit(fonttxt,(SCREEN_WIDTH/2 - w/2, y))
        y += (h*factor)

    for x,y,w,h in coor:
        underlineInitials(screen,WHITE,(x,y),(x+w,y))

    indx = 0
    hof = ""
    while True:
        x,y,w,h = coor[indx]
        initial = enterInitial(screen,font,x,y-h,w,h)
        hof += initial
        underlineInitials(screen,BLACK,(x,y),(x+w,y))
        pygame.display.flip()
        indx += 1
        if indx >= 3:
            break

    # save hall of framer
    topScores(highscores, hof, score)

def enterInitial(screen,font,x,y,w,h):
    inits = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    indx = 0
    exitkey = None

    letter = "A"
    fonttxt = font.render(letter, True, WHITE, BLACK)
    #center letter
    wtmp,htmp = font.size(letter)
    offset = (w - wtmp)/2
    screen.blit(fonttxt,(x+offset,y))
    pygame.display.flip()

    wait = True
    while wait:
        for e in pygame.event.get():
            keys = pygame.key.get_pressed()
            if e.type == QUIT or keys[K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                KEY_DICT = {K_UP:1, K_DOWN:-1}
                if e.key in KEY_DICT:
                    indx += KEY_DICT[e.key]
                    if indx < 0:
                        indx = len(inits)-1
                    if indx >= len(inits):
                        indx = 0
                    letter = inits[indx:indx+1]
                    fonttxt = font.render("W",True,BLACK,BLACK)
                    screen.blit(fonttxt,(x,y))
                    fonttxt = font.render(letter,True,WHITE,BLACK)
                    #center letter
                    wtmp,htmp = font.size(letter)
                    offset = (w - wtmp)/2
                    screen.blit(fonttxt,(x+offset,y))
                    pygame.display.flip()
                if e.key == K_RIGHT:
                    wait = False

    pygame.event.clear((KEYUP,KEYDOWN))
    pygame.key.get_pressed()
    pygame.event.get()
    return letter

def getInitialCoor(font,x,y):
    coor = [(0,0,0,0),(0,0,0,0),(0,0,0,0)]
    txt = "W|W|W"
    w,h = font.size(txt)
    _x = SCREEN_WIDTH/2 - w/2
    lst = list(enumerate(txt))
    for i,letter in lst:
        _w,_h = font.size(letter)
        if i in [0,2,4]:
            coor[i/2] = (_x,y+h,_w,_h)
            _x += _w
        else:
            _x += _w/2
    return coor

def underlineInitials(screen,color,start_pos,end_pos):
    pygame.draw.line(screen,color,start_pos,end_pos,2)

def topScores(topscores, player, score):
    topscores.append((player,score))

    # only top 10
    topscores = sorted(topscores, key=itemgetter(1), reverse=True)[:10]

    try:
        with open('highscores.txt', 'w') as file:
            pickle.dump(topscores, file)
    except IOError as e:
        # doesn't exist
        pass