import random
from rng import *

class Maze(object):
    def __init__(self,roomX,roomY):
        self.rmX = roomX
        self.rmY = roomY
        RNG.seed = 0
        self.rmNumber = (self.rmY << 8) + self.rmX
        self.exitDoors = {}
        self.pillars = ""

    def getPillars(self,):
        RNG.seed = self.rmNumber
        #pillars = [[0 for x in range(2)] for x in range(5)]
        pillars = ""
        for row in range(2):
            for col in range(4):
                RNG.getRandomNumber()
                pillarValue = RNG.getRandomNumber()
                walldirection = self.getWall(pillarValue)
                #pillars[row][col] = walldirection
                pillars += walldirection
        self.pillars = pillars
        return pillars

    """
    Convert the 16 bit number generated from the random number generator
    into a wall direction. This is done by taking the high 8 bits and
    looking at the 2 low bits of this.
    """
    def getWall(self, pillarValue):
        # wall direction: North, South, East, or West
        return {0:"N",1:"S",2:"E",3:"W"}[pillarValue & 0x03]

    def exit(self, door = ""):
        x,y,z = {"S":(0,1,"N"), "N":(0,-1,"S"), "W":(-1,0,"E"), "E":(1,0,"W"), "":(0,0,"")}[door]

        self._exitMazeDoor(self.rmNumber,door)

        # if no exit door then randomly pick a room
        if door == "":
            x = (-1,0,1)[random.randrange(0,3)]
            y = (-1,0,1)[random.randrange(0,3)]
        self.rmX = (self.rmX + x) & 0xFF
        self.rmY = (self.rmY + y) & 0xFF
        self.rmNumber = (self.rmY << 8) + self.rmX

        self._exitMazeDoor(self.rmNumber,z)

    def _exitMazeDoor(self,room,door):
        exits = ""
        try:
            exits = self.exitDoors.pop(room)
        except:
            pass

        exits = exits + door
        self.exitDoors.setdefault(room,exits)
        pass

    def getDoors(self):
        doors = ""
        try:
            doors = self.exitDoors.setdefault(self.rmNumber,doors)
        except:
            pass

        #print( self.rmNumber, doors )
        return doors

"""
close door S  roomY--
close door E  roomX--
close door W  roomX++
close door N  roomY++
"""