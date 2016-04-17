import pygame, spritesheet, random
from pygame.locals import *
from config import *
from animateobj import *
import player
from bullet import *
from grid import *
import math
import cmath    # complex numbers
import itertools


class Robot(AnimateObj):
    grp = pygame.sprite.Group()
    killcnt = 0
    robotcnt = 0
    laserEnable = False

    @staticmethod
    def getGroup():
        return Robot.grp

    @staticmethod
    def killCount():
        return Robot.killcnt

    @staticmethod
    def robotCount():
        return Robot.robotcnt

    @staticmethod
    def newLevel(laser):
        Robot.robotcnt = 0
        Robot.killcnt = 0
        Robot.laserEnable = laser

    @staticmethod
    def robotCollision(robot):
        # check robot to robot collision
        combo = list(itertools.combinations(Robot.getGroup(), 2))
        for a,b in combo:
            if pygame.sprite.collide_rect(a,b) == True:
                if a in Robot.getGroup():
                    if type(a) is Robot:
                        return True
                if b in Robot.getGroup():
                    if type(b) is Robot:
                        return True

        # check new robot collision with robots
        collidelist = pygame.sprite.spritecollide(robot, Robot.getGroup(), False)
        for collide in collidelist:
            if type(collide) is not Player:
                self.player.electrocute()
                break
            else:
                pass


    def __init__(self, color, cbRobot, player, grid, pillars, walls, imagefiles, rect, count, frame = 5, colorkey=BLACK, scale=2):
        super(Robot,self).__init__()
        ss = spritesheet.spritesheet(imagefiles['robot'])
        self.images =  ss.load_strip(rect, count, colorkey)
        self.frameupdate = self.frame = frame
        self.cbRobot = cbRobot
        self.imagefiles = imagefiles
        self.active = False
        self.pillars = pillars
        self.cellX = 0
        self.cellY = 0
        self.grid = grid

        for i in range(count):
            image = self.images[i]
            image.set_colorkey(colorkey, RLEACCEL)
            w,h = image.get_size()
            cropped_image = image.subsurface(0,0,w,h)
            scale_image = pygame.transform.scale(cropped_image,(scale*w,scale*h))
            self.images[i] = scale_image

        self.setcolor(color)

        self.rect = self.images[0].get_rect()

        self.addpattern("roving_eye", [0,1,2,1,0,5,4,5])
        self.addpattern("east", [7,6,6])
        self.addpattern("south", [0,8,0,9])
        self.addpattern("west", [10,11,11])
        self.addpattern("north", [12,13,12,14])
        self.setpattern("roving_eye")

        self.reset(walls,grid)
        self.player = player

        self.timer = pygame.time.get_ticks()
        self.cooldown = 600
        Robot.grp.add(self)
        Robot.robotcnt += 1

    def reset(self,walls,grid):
        w,h = self.rect.width, self.rect.height
        self.rect.width *= 2
        self.rect.height *= 2
        while True:
            # make sure rect in boundry
            rx = random.randrange(1,38)
            ry = random.randrange(1,21)

            # make sure robot not on wall
            if rx in (7,8,15,16,23,24,31,32):
                continue
            if ry in (6,7,14,15):
                continue
            x,y = grid.getScreenCoor(rx, ry)

            cell = grid.getCell(rx,ry)
            if cell.reachable == False:
                continue

            cells = grid.get_adjacent_cells(cell)
            for adjcell in cells:
                if adjcell.reachable == False:
                    cell = None
                    break
            if cell is None:
                continue

            # make sure robot starting position isn't near player starting position
            if grid.getQuadrant(x,y) in ((2,0),(0,1),(4,1),(2,2)):
                continue

            self.rect.x = x
            self.rect.y = y

            # check if new robot will collide with existing robots
            if pygame.sprite.spritecollideany(self, Robot.getGroup()):
                continue

            # make sure robot not on wall
            # same code in main...share here?
            #if pygame.sprite.spritecollideany(self, walls):
            #    continue

            cell.reachable = False
            self.cellX = rx
            self.cellY = ry

            break

        self.rect.width = w
        self.rect.height = h

        # random image to start with
        self.index >= random.randrange(len(self.pattern))


    def kill(self):
        super(Robot,self).kill()
        if type(self) == Robot:
            Robot.killcnt += 1

            # check for bonus points
            if Robot.killcnt == Robot.robotcnt:
                bonus = 10 * Robot.killcnt
                event = pygame.event.Event(BONUS_POINTS, bonuspoints = bonus)
                pygame.event.post(event)
            elif (Robot.robotcnt - Robot.killcnt) <= 2:
                # speed up robots when only two or less exist
                for robot in Robot.getGroup():
                    if type(robot) is Robot:
                        if robot.frameupdate >= 2:
                            robot.frameupdate -= 1

    def update(self):
        self.frame -= 1
        if self.frame == 0:
            self.frame = self.frameupdate
            super(Robot,self).update()

            deltaX, deltaY = 0,0

            if self.active:
                rx, ry = self.grid.getCellCoor(self.rect.x, self.rect.y)
                if rx == self.cellX and ry == self.cellY:
                    px, py = self.grid.getCellCoor(self.player.rect.centerx,self.player.rect.centery)
                    if rx != px or ry != py:
                        maze = AStar()
                        maze.init_grid(self.grid,(rx,ry),(px,py))
                        path = maze.solve()

                        if path is not None:
                            rx,ry = path.pop(1)
                            self.cellX = rx
                            self.cellY = ry

                        del maze
                else:
                    rx = self.cellX
                    ry = self.cellY

                rx,ry = self.grid.getScreenCoor(rx, ry)
                waypoint = complex(rx,ry)
                robot = complex(self.rect.x, self.rect.y)
                cc = waypoint - robot

                sign = lambda x: (x > 0) - (x < 0)
                deltaX = sign(int(cc.real))*2
                self.rect.x += deltaX
                deltaY = sign(int(cc.imag))*2
                self.rect.y += deltaY

            pattern = "roving_eye"
            if (deltaX == 0) & (deltaY == 0):
                pattern = "roving_eye"
            elif deltaX > 0:
                pattern = "east"
            elif deltaX < 0:
                pattern = "west"
            elif deltaY < 0:
                pattern = "north"
            elif deltaY > 0:
                pattern = "south"

            if pattern <> self.patternkey:
                self.setpattern(pattern)

            # fire laser only if cooldown has been 0.6 secs
            now = pygame.time.get_ticks()
            if now - self.timer > self.cooldown:
                if Robot.laserEnable:
                    self.shoot()
                self.timer = now


    def sameCell(self):
        bRet = False
        robotCell = self.getCell(self.rect)
        playerCell = self.getCell(self.player.rect)
        if robotCell == playerCell:
            bRet = True
        return bRet

    def sameRow(self):
        bRet = False
        robotRow = self.getRow(self.rect)
        playerRow = self.getRow(self.player.rect)
        if robotRow == playerRow:
            bRet = True
        return bRet

    def sameCol(self):
        bRet = False
        robotCol = self.getCol(self.rect)
        playerCol = self.getCol(self.player.rect)
        if robotCol == playerCol:
            bRet = True
        return bRet

    def getRow(self, rect):
         return (rect.y - MAZE_YMIN)/BORDER_VSEGMENT

    def getCol(self, rect):
        return (rect.x - MAZE_XMIN)/BORDER_HSEGMENT

    def getCell(self, rect):
        col = (rect.x - MAZE_XMIN)/BORDER_HSEGMENT
        row = (rect.y - MAZE_YMIN)/BORDER_VSEGMENT
        return (row*5)+col

    def getAngle(self, x1, y1, x2, y2):
        # Return value is 0 for right, 90 for up, 180 for left, and 270 for down (and all values between 0 and 360)
        rise = y1 - y2
        run = x1 - x2
        angle = math.atan2(run, rise)   # get the angle in radians
        angle = angle * (180 / math.pi) # convert to degrees
        return angle

    # robots fire on player if aligned in any of the 8 directions
    def shoot(self):
        direction = None
        # detect horizontal alignment
        if (self.rect.centery >= self.player.rect.top) and (self.rect.centery <= self.player.rect.bottom):
            direction = ("W", "E")[self.rect.centerx <= self.player.rect.centerx]
        # detect vertical alignment
        elif (self.rect.centerx >= self.player.rect.left) and (self.rect.centerx <= self.player.rect.right):
            direction = ("N", "S")[self.rect.centery <= self.player.rect.centery]
        # detect diagonal alignment
        """
        if abs(self.rect.centerx - self.player.rect.centerx) == abs(self.rect.centery - self.player.rect.centery):
            if self.rect.centery <= self.player.rect.centery:
                direction = ("SE","SW")[self.rect.centerx >= self.player.rect.centerx]
            else:
                direction = ("NE","NW")[self.rect.centerx >= self.player.rect.centerx]
        """
        if direction is None:
            angle = self.getAngle(self.rect.centerx, self.rect.centery, self.player.rect.centerx, self.player.rect.centery)
            if (angle >= 35.0) and (angle <= 55.0):
                direction = "NW"
            elif (angle >= 125.0) and (angle <= 145.0):
                direction = "SW"
            elif (angle >= -145.0) and (angle <= -125.0):
                direction = "SE"
            elif (angle >= -55.0) and (angle <= -35.0):
                direction = "NE"

        self.fire(direction)

    def fire(self,direction):
        # FIX THIS!!! change the hard-coded nums to defines
        x,y = 0,0
        if self.patternkey == "east":
            x, y = {"NE":(10,-10), "E":(8,0), "SE":(10,0)}.get(direction,(0,0))
        elif self.patternkey == "west":
            x, y = {"SW":(-20,0), "W":(-20,0), "NW":(-20,-10)}.get(direction,(0,0))
        elif self.patternkey in ("north","south"):
            x, y = {"N":(8,-20),"S":(8,6)}.get(direction,(0,0))

        if (x <> 0) or (y <> 0):
            bullet = RobotBullet(self.color, direction, self.rect.centerx + x, self.rect.centery + y, self.imagefiles['bullets'] )
            if bullet <> None:
                if self.cbRobot <> None:
                    self.cbRobot("FIRE", bullet)

    def draw(self):
        pass

    def explode(self):
        pass

class RobotBullet(Bullet):
    def __init__(self, color, direction, x, y, filename, speed=8, count=1, colorkey=None, scale=2):
        super(RobotBullet,self).__init__(color, direction, x, y, filename, speed=4, count=1, colorkey=BLACK, scale=2)

class RobotExplode(AnimateObj):
    def __init__(self, robot, cbExplode, filename, rect, count, colorkey=BLACK, scale=2):
        super(RobotExplode,self).__init__(cbExplode)
        ss = spritesheet.spritesheet(filename)
        self.images =  ss.load_strip(rect, count, colorkey)
        self.frame = 10

        for i in range(count):
            image = self.images[i]
            image.set_colorkey(colorkey)  #black is transparent
            w,h = image.get_size()
            cropped_image = image.subsurface(0,0,w,h)
            scale_image = pygame.transform.scale(cropped_image,(scale*w,scale*h))
            self.images[i] = scale_image

        self.rect = self.images[0].get_rect()
        self.rect.x = robot.rect.x
        self.rect.y = robot.rect.y
        self.setcolor(robot.color)

        self.addpattern("explode", [0,1,2])
        self.setpattern("explode")
        Robot.grp.add(self)

    def update(self):
        self.frame -= 1
        if self.frame == 0:
            self.frame = 5
            super(RobotExplode,self).update()

    def draw(self):
        pass