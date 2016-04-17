import sys, os, pygame
from pygame.locals import *
import heapq
from config import *

class Cell(object):
    def __init__(self, x, y, reachable):
        """Initialize new cell.
        @param reachable is cell reachable? not a wall?
        @param x cell x coordinate
        @param y cell y coordinate
        @param g cost to move from the starting cell to this cell.
        @param h estimation of the cost to move from this cell
                 to the ending cell.
        @param f f = g + h
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

        self.screenX = MAZE_XMIN-4 + x*16
        self.screenY = MAZE_YMIN+8 + y*22


"""
0: empty cell
1: unreachable cell: e.g. wall
2: ending cell
3: visited cell
"""

class Grid(object):
    def __init__(self, width, height, walls, cols=5, rows=3):
        self.width = width
        self.height = height
        self.walls = walls
        self.gridcells = []
        self.wallcells = []

        for x in range(width):       # 0-39
            for y in range(height):   # 0-21
                self.gridcells.append(Cell(x,y,True))

        for i, w in list(enumerate(walls[:])):
            if w == "N":
                #x = list(range(int(width/cols),width,int(width/cols)))[i%4]
                #for x in {0:(7,8),1:(15,16),2:(23,24),3:(31,32)}[i%4]:
                x = (8,16,24,32)[i%4]
                #print( "N", list(range(int(i/4)*int(height/rows),int(i/4)*int(height/rows)+int(height/rows)+1)))
                #for y in list(range(int(i/4)*int(height/rows),int(i/4)*int(height/rows)+int(height/rows)+1)):
                for y in {0:(0,1,2,3,4,5,6),1:(6,7,8,9,10,11,12,13,14)}[int(i/4)]:
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            elif w == "S":
                #for x in {0:(7,8),1:(15,16),2:(23,24),3:(31,32)}[i%4]:
                x = (8,16,24,32)[i%4]
                #x = list(range(int(width/cols),width,int(width/cols)))[i%4]
                for y in {0:(6,7,8,9,10,11,12,13,14),1:(14,15,16,17,18,19,20,21)}[int(i/4)]:
                #print( "S", list(range(int(height/rows)-1 + int(i/4)*int(height/rows),((int(i/4)+2)*int(height/rows) + 1 ))))
                #for y in list(range(int(height/rows)-1 + int(i/4)*int(height/rows),((int(i/4)+2)*int(height/rows) + 1))):
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            elif w == "E":
                #for y in {0:(6,7),1:(14,15)}[i/4]:
                #y = (6,14)[i/4]:
                y = (6,14)[int(i/4)]
                #for x in list(range(int(width/cols)+2)):
                    #x += int(width/cols)*((i%4)+1)
                    #if x >= width:
                        #break
                for x in {0:(8,9,10,11,12,13,14,15,16),1:(16,17,18,19,20,21,22,23,24),2:(24,25,26,27,28,29,30,31,32),3:(32,33,34,35,36,37,38,39)}[i%4]:
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            elif w == "W":
                y = (6,14)[int(i/4)]
                for x in {0:(0,1,2,3,4,5,6,7,8),1:(8,9,10,11,12,13,14,15,16),2:(16,17,18,19,20,21,22,23,24),3:(24,25,26,27,28,29,30,31,32)}[i%4]:
                #for x in list(range(int(width/cols)+2)):
                    #x += int(width/cols)*(i%4)
                    cell = self.gridcells[x * self.height + y]
                    cell.reachable = False
                    self.wallcells.append((x,y))
            else:
                pass

    def getScreenCoor(self,x,y):
        cell = self.gridcells[x * self.height + y]
        return cell.screenX, cell.screenY

    def getCellCoor(self,x,y):
        return (x - (MAZE_XMIN-4))/16, (y - (MAZE_YMIN+8))/22

    def getCell(self,x,y):
        return self.gridcells[x * self.height + y]

    def getQuadrant(self,x,y):
        return int((x-MAZE_XMIN)/BORDER_HSEGMENT), int((y-MAZE_YMIN)/BORDER_VSEGMENT)

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.width-1:
            cells.append(self.getCell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.getCell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.getCell(cell.x-1, cell.y))
        if cell.y < self.height-1:
            cells.append(self.getCell(cell.x, cell.y+1))
        return cells

    """
    def drawGrid(self,screen):
        for i in range(len(self.gridcells)):
            x,y = self.gridcells(i)
        for x in range(MAZE_XMIN,MAZE_XMAX,16):
            for y in range(MAZE_YMIN,MAZE_YMAX ,22):
                pygame.draw.line(screen, RED, (x, y), (MAZE_XMAX, y), (1))
                pygame.draw.line(screen, RED, (x, y), (x, MAZE_YMAX), (1))
                print(x,y)


    # make sure rect in boundry
            self.rect.x = random.randrange(MAZE_XMIN+self.rect.width,  MAZE_XMAX-self.rect.width)
            self.rect.y = random.randrange(MAZE_YMIN+self.rect.height, MAZE_YMAX-self.rect.height)

    """

class AStar(object):
    def __init__(self):
        # open list
        self.opened = []
        heapq.heapify(self.opened)
        # visited cells list
        self.closed = set()
        # grid cells
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    def init_grid(self, grid, start, end):
        """Prepare grid cells, walls.
        @param width grid's width.
        @param height grid's height.
        @param walls list of wall x,y tuples.
        @param start grid starting point x,y tuple.
        @param end grid ending point x,y tuple.
        """
        self.grid_height = grid.height
        self.grid_width = grid.width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in grid.wallcells:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    def get_heuristic(self, cell):
        """Compute the heuristic value H for a cell.
        Distance between this cell and the ending cell multiply by 10.
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_cell(self, x, y):
        """Returns a cell from the cells list.
        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        try:
            cell = self.cells[x * self.grid_height + y]
        except IndexError, message:
            print(x,y)
            raise SystemExit, message
        return cell

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.grid_width-1:
            cells.append(self.get_cell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        if cell.y < self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def get_path(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            if cell is None:
                pass
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """Update adjacent cell.
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def display_path(self):
        cell = self.end
        while cell.parent is not self.start:
            cell = cell.parent
            print 'path: cell: %d,%d' % (cell.x, cell.y)


    def solve(self):
        """Solve maze, find path to ending cell.
        @returns path or None if not found.
        """
        # add starting cell to open heap queue
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list so we don't process it twice
            self.closed.add(cell)
            # if ending cell, return found path
            if cell is self.end:
                #self.display_path()
                return self.get_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))
