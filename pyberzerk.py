__author__ = 'TerryO'


import sys, os, platform, pygame
from pygame.locals import *
from config import *
from robot import *
from player import *
from bullet import *
from otto import *
from maze import *
from wall import *
from lives import *
from score import *
from utils import *
from grid import *
import itertools


#--- Global constants ---
SCREEN_RECT = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)   # screen dimensions

# image cache
IMAGEKEYS = ['player', 'robot', 'otto', 'robotexplode', 'lives', 'bullets', 'icon']         #image keys

DIRECT_DICT = {K_LEFT : 0x01, K_RIGHT : 0x02, K_UP : 0x04, K_DOWN : 0x08, K_SPACE : 0x10}   # keyboard keys

GAME_STATES = ["HighScores", "Cntrls", "Play"]  # game states

screen = None


# class handles our game states(screens)
class GameState:
    def __init__(self):
        # prepare pygame environment
        os.environ['SDL_VIDEO_CENTERED'] = '1'      # center the screen
        pygame.init()
        pygame.display.set_caption(CAPTION)
        pygame.mouse.set_visible(0)
        pygame.font.init()

        # get directory where game & images are located
        path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(path)

        # images(sprites)
        global imagefiles
        imagefiles = {}
        try:
            imagefiles = {key: os.path.join('images', "{}.png".format(key)) for key in IMAGEKEYS}
        except:
            pass

        global screen
        screen = pygame.display.set_mode(SCREEN_RECT.size)

        # if platform.system() == "Windows":
        icon = pygame.image.load(imagefiles['icon']).convert_alpha()
        pygame.display.set_icon(icon)

        self.game = None

    # highscores state
    def HighScore(self):
        gamestate = "Play"
        keys = highScoresScreen(screen)
        if keys[K_F1]:
            gamestate = "Cntrls"
        self.Go(gamestate)

    # controls help state
    def Cntrls(self):
        gameCntrls(screen)
        self.Go("HighScore")

    # play game state
    def Play(self):
        if self.game == None:
            self.game = Game()

        """
         robot color  level   bullet
         DARK YELLOW  0       0
         RED          500     1
         DARK CYAN    1500    2
         GREEN        3K      3
         DARK PURPLE  4.5K    4
         LIGHT YELLOW 6K      5
         WHITE        7.5K    1 *fast bullets
         DARK CYAN    10K     2
         LIGHT PURPLE 11K     3
         GRAY         13K     4
         DARK YELLOW  15K     5
         RED          17K     5
         LIGHT CYAN   19K     5
        """
        robotcolors = ((YELLOW, False, 0, 500, 5), (RED, True, 1, 1500, 4), (CYAN, True, 2, 3000, 3),
                       (GREEN, True, 3, 4500, 2), (PURPLE, True, 4, 6000, 1), (YELLOW, True, 5, 7500, 1),
                       (WHITE, True, -1, 10000, 1), (LIGHTSKYBLUE, True, -2, 11000, 1), (PURPLE, True, -3, 13000, 1),
                       (GRAY, True, -4, 15000, 1), (YELLOW, True, -5, 17000, 1), (RED, True, -5, 19000, 1),
                       (LIGHTSKYBLUE, True, -5, 999999, 1)
                       )

        # maxbullets is currently not used...need to add this feature
        for color, fire, maxbullets, max_score, frameupdate in robotcolors:
            if  Score.score < max_score:
                break

        self.game.run(color, fire, frameupdate)

        gamestate = "Play"
        if self.game.lives <= 0:
            if gameOver(screen,Score.score):
                gamestate = "HighScore"
            Score.score = 0
            tmp = sys.getrefcount(self.game)
            del self.game
            self.game = None

        self.Go(gamestate)

    # we are done
    def Quit(self):
        pygame.quit()
        sys.exit()

    def Go(self,gamestate):
        if hasattr(self,gamestate):
            state = getattr(self,gamestate)
            state()

class Game:
    def __init__(self):
        self.done = False
        self.event_type = None
        self.shotflg = False
        self.keycnt = 0
        self.movdir = 0
        self.maze = Maze(0x53,0x31)   # starting room X,Y
        self.mazeexit = None
        self.lives = MAX_LIVES
        self.bonuspts = None
        self.keys = pygame.key.get_pressed()

    def process_events(self):
        for e in pygame.event.get():
            if e.type == QUIT or self.keys[K_ESCAPE]:
                self.done = True
                pygame.quit()
                sys.exit()
                break
            elif e.type == SPAWN_OTTO:
                self.spawnOtto()
            elif e.type == ROBOT_ACTIVE:
                self.robotActive()
            elif e.type == PLAYER_EXIT:
                self.playerExit(e.mazeexit)
            elif e.type == BONUS_POINTS:
                self.bonusPoints(e.bonuspoints)
            elif e.type == BONUS_LIFE:
                self.bonusLife()
            elif e.type == PLAYER_ELECTROCUTED:
                self.playerElectrocuted()
            elif e.type in (KEYUP,KEYDOWN):
                self.keys = pygame.key.get_pressed()
                if self.keys[K_F1]:
                    gamePause(screen)
                if self.keys[K_F2]:
                    gameFPS.toggleDisplay()
                if e.type == KEYDOWN:
                    self.keycnt += 1
                    if e.key in DIRECT_DICT:
                        self.movdir |= DIRECT_DICT[e.key]
                elif e.type == KEYUP:
                    self.keycnt -= 1
                    if e.key in DIRECT_DICT:
                        self.movdir &= ~DIRECT_DICT[e.key]

                # checking if left modifier is pressed
                if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    pass


    def playerElectrocuted(self):
        pygame.time.set_timer(PLAYER_ELECTROCUTED,0) # kill timer
        self.maze.exit()
        self.mazeexit = None
        self.done = True
        for obj in self.sprites:
            if type(obj) is Lives:
                if obj.life == self.lives:
                    obj.kill()
                    break
        self.lives -= 1
        if self.lives <= 0:
            for obj in self.wall2grp:
                obj.kill()
            self.player.kill()
            self.refreshSprites()
        else:
            screenMazeClear(screen)
        self.spriteCleanUp()

    def electrocute(self):
        if self.player.patternkey <> "electrocuting":
            # disable any active timer(s)
            pygame.time.set_timer(SPAWN_OTTO,0)
            pygame.time.set_timer(ROBOT_ACTIVE,0)

            # put player in electrocut mode
            self.player.electrocute()
            pygame.time.set_timer(PLAYER_ELECTROCUTED, 1000)  # 1sec

            # robot(s) stop firing
            Robot.laserEnable = False

            for obj in self.wall2grp:
                obj.kill()

    def robot_explode(self,robot):
        # after robot explode sprite is done this is it's callback
        def callback(robot):
            robot.kill()        # get rid of explode sprite

        explode = RobotExplode(robot, callback, imagefiles['robotexplode'], ROBOTEXPLODE_RECT, ROBOTEXPLODE_SPRITES )
        self.sprites.add(explode)
        robot.kill()            # get rid of robot sprite
        self.score.addpoints(ROBOT_KILL_POINTS)

    def bonusPoints(self, bonus):
        points = Bonus(GRAY, bonus)
        self.sprites.add(points)

    def bonusLife(self):
        self.lives += 1
        life = Lives(self.lives, imagefiles['lives'], LIVES_RECT, GREEN)
        self.sprites.add(life)

    def check_collisions(self):
        # check bullet collision with robots/otto
        collidedict = pygame.sprite.groupcollide(self.bullets, Robot.getGroup(), False, False)
        if collidedict:
            for bullet in collidedict.keys():
                bullet.kill()
                for value in collidedict.values():
                    for robot in value:
                        if type(robot) is Robot:
                            self.robot_explode(robot)
                        else:
                            pass

        # check bullet collision with player
        collidedict = pygame.sprite.groupcollide(self.bullets, self.playergrp, False, False)
        if collidedict:
            for bullet in collidedict.keys():
                if type(bullet) is RobotBullet:
                    bullet.kill()
                    for value in collidedict.values():
                        for player in value:
                            if type(player) is Player:
                                self.electrocute()
                                return
                            else:
                                pass

        # check bullet to bullet collision
        combo = list(itertools.combinations(self.bullets, 2))
        for a,b in combo:
            if pygame.sprite.collide_rect(a,b):
                a.kill()    # remove from grp
                b.kill()

        # check bullet collision with wall
        for bullet in self.bullets:
            if pygame.sprite.spritecollideany(bullet, self.wallgrp):
                bullet.kill()

        # check robot collision with wall
        collidedict = pygame.sprite.groupcollide(Robot.getGroup(), self.wallgrp, False, False)
        if collidedict:
            for robot in collidedict.keys():
                if type(robot) is Robot:
                    self.robot_explode(robot)

        # remove any old wall warnings
        for x in self.wall2grp:
            x.kill()

        # warn player if close to wall by highlighting wall area
        r = self.player.rect.copy()
        self.player.rect = self.player.rect.inflate(16, 16)
        collide_list = pygame.sprite.spritecollide(self.player, self.wallgrp, False)
        for collide in collide_list:
            c = collide.rect.clip(self.player.rect)
            if collide.rect.w == 8:
                c.left = collide.rect.left
                c.w = 8
            else:
                c.top = collide.rect.top
                c.h = 8
            wall2 = WallObject(screen, GREEN, c)
            self.sprites.add(wall2)
            self.wall2grp.add(wall2)

        self.player.rect = r.copy()

        # check player collision with wall
        if pygame.sprite.spritecollideany(self.player, self.wallgrp):
            self.electrocute()

        # check player collision with robots
        collide = pygame.sprite.spritecollideany(self.player, Robot.getGroup())
        if collide:
            if type(collide) is Robot:
                self.robot_explode(collide)
            self.electrocute()

        # check robot to robot collision
        combo = list(itertools.combinations(Robot.getGroup(), 2))
        for a,b in combo:
            if pygame.sprite.collide_rect(a,b):
                if type(a) is Robot:
                    self.robot_explode(a)
                if type(b) is Robot:
                    self.robot_explode(b)

    def spawnOtto(self):
        pygame.time.set_timer(SPAWN_OTTO,0) # disable timer
        otto = Otto(self.levelcolor, self.player, imagefiles['otto'], OTTO_RECT, OTTO_SPRITES )
        self.sprites.add(otto)
        Robot.getGroup().add(otto)

    def robotActive(self):
        pygame.time.set_timer(ROBOT_ACTIVE,0) # disable timer

        # wake up robots
        for robot in Robot.getGroup():
            if type(robot) == Robot:
                robot.active = True

    def playerExit(self,mazeexit):
        pygame.time.set_timer(SPAWN_OTTO,0)     # disable any active timer(s)
        pygame.time.set_timer(ROBOT_ACTIVE,0)
        screenScroll(screen,mazeexit,self.levelcolor)
        self.maze.exit(mazeexit)
        self.mazeexit = mazeexit
        self.done = True

        for obj in self.sprites:
            if type(obj) == Bonus:
                obj.kill()
                break

        self.spriteCleanUp()

    def spriteCleanUp(self):
        # clean up sprites
        self.bullets.empty()
        self.wallgrp.empty()
        self.wall2grp.empty()
        self.playergrp.empty()
        self.explodegrp.empty()
        self.lifegrp.empty()
        Robot.getGroup().empty()
        self.sprites.empty()
        del self.bullets
        del self.wallgrp
        del self.wall2grp
        del self.playergrp
        del self.explodegrp
        del self.lifegrp
        del self.sprites
        del self.score
        del self.gamefps

    def run(self, levelcolor, robotLaser, frameupdate):
        self.levelcolor = levelcolor

        # keep track of sprites
        self.explodegrp = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        Bullet.bulletcnt = BULLETS_MAX
        self.wallgrp = pygame.sprite.Group()
        self.wall2grp = pygame.sprite.Group()
        self.playergrp = pygame.sprite.GroupSingle()

        self.sprites = pygame.sprite.LayeredUpdates(self.wallgrp, self.playergrp,self.explodegrp)
        self.lifegrp = pygame.sprite.Group()

        door = {"E":"W","W":"E","N":"S","S":"N"}.get(self.mazeexit,"W")
        self.player = Player(door, PLAYER_COLOR, imagefiles['player'], PLAYER_RECT, PLAYER_SPRITES)
        self.sprites.add(self.player)
        self.playergrp.add(self.player)

        self.score = Score(GREEN)
        self.sprites.add(self.score)

        self.gamefps = gameFPS(GREEN)
        self.sprites.add(self.gamefps)

        self.Arena(screen,self.maze,levelcolor)
        grid = Grid(40, 22, self.maze.pillars)

        def robotCallBack(cmd, *argv):
            if cmd == "FIRE":
                bullet = argv[0]
                self.sprites.add(bullet)
                self.bullets.add(bullet)

        # create robots
        Robot.newLevel(robotLaser)
        for i in range(random.randrange(MIN_ROBOTS,MAX_ROBOTS)):
            robot = Robot(levelcolor, robotCallBack, self.player, grid, self.maze.pillars, self.wallgrp, imagefiles, ROBOT_RECT, ROBOT_SPRITES, frameupdate )
            self.sprites.add(robot)

        # create lives
        for i in range(2, self.lives+1):
            life = Lives(i, imagefiles['lives'], LIVES_RECT, GREEN)
            self.sprites.add(life)

        # keep track of time
        clock = pygame.time.Clock()

        self.timer = pygame.time.get_ticks()
        self.cooldown = 600

        # set timer event for Otto
        pygame.time.set_timer(SPAWN_OTTO,1500*Robot.robotcnt) # 1.5sec/robot

        # set timer event for robot movement
        pygame.time.set_timer(ROBOT_ACTIVE,3000) # 3sec

        # maze loop
        self.done = False
        while not self.done:
            now = pygame.time.get_ticks()
            self.process_events()

            if self.done:
                break

            gameFPS.clock = clock.get_fps()

            if self.player.patternkey <> "electrocuting":
                self.player.mov(self.movdir)

                if self.movdir & 0x10:
                    # fire laser only if cooldown has been 0.6 secs
                    if now - self.timer > self.cooldown:
                        bullet = self.player.fire(levelcolor, imagefiles['bullets'])
                        if bullet <> None:
                            self.sprites.add(bullet)
                            self.bullets.add(bullet)
                            self.timer = now

            self.check_collisions()
            self.refreshSprites()
            clock.tick(FPS)     # maintain frame rate

    def refreshSprites(self):
        # used to erase the sprite
        def clear_callback(surf, rect):
            surf.fill(BLACK, rect)
            pass

        # erase previous positions
        self.sprites.clear(screen, clear_callback)

        # update sprites
        self.sprites.update()

        # debugAIgrid()

        # redraw sprites
        dirty = self.sprites.draw(screen)
        pygame.display.update(dirty)

    def debugAIgrid(self):
        # debug code for robot AI grid
        for x in range(MAZE_XMIN-4,MAZE_XMAX+16,16):
        #for x in range(MAZE_XMIN, MAZE_XMAX,24):
            for y in range(MAZE_YMIN+8,MAZE_YMAX ,22):
            #for y in range(MAZE_YMIN, MAZE_YMAX,24):
                pygame.draw.line(screen, RED, (x, y), (MAZE_XMAX, y), (1))
                pygame.draw.line(screen, RED, (x, y), (x, MAZE_YMAX), (1))

    # build border walls and maze walls
    def Arena(self, screen, maze, doorcolor=None):
        # borders: west top, west bottom, east top, east bottom, left top, left bottom, right top, right bottom
        borders = [
            (BORDER_XMIN, BORDER_YMIN, WALLTHICKNESS, BORDER_VSEGMENT + WALLTHICKNESS),
            (BORDER_XMIN, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*2, WALLTHICKNESS, BORDER_VSEGMENT),
            (BORDER_XMAX, BORDER_YMIN, WALLTHICKNESS, BORDER_VSEGMENT + WALLTHICKNESS),
            (BORDER_XMAX, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*2, WALLTHICKNESS, BORDER_VSEGMENT),
            (BORDER_XMIN, BORDER_YMIN, WALLTHICKNESS + BORDER_HSEGMENT*2, WALLTHICKNESS),
            (BORDER_XMIN, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*3, WALLTHICKNESS + BORDER_HSEGMENT*2, WALLTHICKNESS),
            (BORDER_XMIN + WALLTHICKNESS + BORDER_HSEGMENT*3, BORDER_YMIN, WALLTHICKNESS + BORDER_HSEGMENT*2, WALLTHICKNESS),
            (BORDER_XMIN + WALLTHICKNESS + BORDER_HSEGMENT*3, BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT*3, BORDER_HSEGMENT*2 + WALLTHICKNESS, WALLTHICKNESS)
        ]

        for left,top,width,height in borders:
            wall = WallObject(screen, WALL_COLOR, pygame.Rect(left,top,width,height))
            self.sprites.add(wall)
            self.wallgrp.add(wall)

        PILLAR_HSEGMENT = BORDER_HSEGMENT
        PILLAR_VSEGMENT = BORDER_VSEGMENT
        HPILLAR = (PILLAR_HSEGMENT, WALLTHICKNESS)
        VPILLAR = (WALLTHICKNESS, PILLAR_VSEGMENT)

        pillars = maze.getPillars()
        i = 0
        for p in pillars[:]:
            fx,fy  = {0:(1,1), 1:(2,1), 2:(3,1), 3:(4,1), 4:(1,2), 5:(2,2), 6:(3,2), 7:(4,2)}[i]
            x = MAZE_XMIN + PILLAR_HSEGMENT*fx
            y = MAZE_YMIN + PILLAR_VSEGMENT*fy
            x_offset,y_offset,w,h = 0,0,0,0

            if p == "N":
                w,h = VPILLAR
                h += {1:WALLTHICKNESS}.get(i,0)
                y_offset -= PILLAR_VSEGMENT
                y_offset += {1:-WALLTHICKNESS}.get(i,0)

            elif p == "S":
                w,h = VPILLAR
                h += {5:WALLTHICKNESS}.get(i,0)

            elif p == "E":
                w,h = HPILLAR
                w += WALLTHICKNESS
                y_offset += {0:-WALLTHICKNESS,1:-WALLTHICKNESS,2:-WALLTHICKNESS,3:-WALLTHICKNESS}.get(i,0)

            elif p == "W":
                w,h = HPILLAR
                w += WALLTHICKNESS
                x_offset -= PILLAR_HSEGMENT
                y_offset += {0:-WALLTHICKNESS,1:-WALLTHICKNESS,2:-WALLTHICKNESS,3:-WALLTHICKNESS}.get(i,0)

            else:
                    pass
            i += 1

            if p <> "O":
                rect = pygame.Rect(x+x_offset, y+y_offset, w, h)
                mazewall = WallObject(screen, WALL_COLOR, rect)
                self.sprites.add(mazewall)
                self.wallgrp.add(mazewall)

        # NOTE: exit door is opposite of where player exited maze
        x,y,w,h = 0,0,0,0
        doors = maze.getDoors()
        for door in doors[:]:
            if door in ("E", "W"):
                y = BORDER_YMIN + WALLTHICKNESS + BORDER_VSEGMENT
                w,h = WALLTHICKNESS/2, BORDER_VSEGMENT
                if door == "E":
                    x = MAZE_XMAX + WALLTHICKNESS/4
                else:
                    x = BORDER_XMIN + WALLTHICKNESS/4

            elif door in ("N", "S"):
                x = BORDER_XMIN + WALLTHICKNESS + BORDER_HSEGMENT*2
                w,h = BORDER_HSEGMENT, WALLTHICKNESS/2
                if door == "N":
                    y = BORDER_YMIN + WALLTHICKNESS/4
                else:
                    y = MAZE_YMAX + WALLTHICKNESS/4

            rect = pygame.Rect(x, y, w, h)
            mazewall = WallObject(screen, doorcolor, rect)
            self.sprites.add(mazewall)
            self.wallgrp.add(mazewall)


def main():
    gs = GameState()
    gs.Go("HighScore")

if __name__ == "__main__":
    main()
    sys.exit()
