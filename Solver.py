import numpy as np
import hashlib
import copy
import datetime

# Notation: [ROW][COL]
# Note: Add Forbidden Cells to improve the efficiency
#       Check duplicate state in the search tree, ?keep DEPTH info

MAX_STEPS = 28  
MAX_DEPTH = 6
MAP_ROW = 8
MAP_COL = 8
FORBIDDEN = [[1,4],[1,5],[2,1],[3,1],[4,6],[5,6],[7,2],[7,3]]

g_para_duplicate_state_count = 0
g_para_duplicate_state_count2 = 0

def isNotForbidden( pos):
    return ( pos not in FORBIDDEN )

class STATE:
    
    def __init__( self):
        pass

    def setup( self, mapstr):

        i=-1
        j=0

        box=[]
        wall=[]

        for c in mapstr:
            if( c=='#'):
               i=i+1
               j=0
               continue

            if( c=='P'):
                player = [i,j]
                j=j+1
                continue

            if( c=='W'):
                wall.append([i,j])
                j=j+1
                continue

            if( c=='B'):
                box.append([i,j])
                j=j+1
                continue

            j=j+1

        self.set_wall( wall)
        self.set_box( box)
        self.set_player( player)

        #print( self._player)
        #print( self._wall)
        #print( self._box)

    def set_goal( self, lst):
        self._goal = np.array( lst, dtype='b')

    def set_box( self, lst):
        self._box = np.array( lst, dtype='b')

    def set_player( self, pos):
        self._player = np.array( pos, dtype='b')

    def set_wall( self, lst):
        self._wall = np.array( lst, dtype='b')

    def get_hexdigest( self):
        m = hashlib.sha256()
        m.update( self._player.tobytes())
        #TODO: possible different orders for same positions of boxes
        m.update( self._box.tobytes())  
        return m.hexdigest()
    
    # print( "Move Box:", box_no, "Steps:", steps, "Dir:", mov_dir)
    def moveBox( self, box_no, mov_dir):

        self._player[0] = self._box[box_no][0] 
        self._player[1] = self._box[box_no][1]

        self._box[box_no][0] += mov_dir[0] 
        self._box[box_no][1] += mov_dir[1]
    
    def matchGoal( self, goal):

        for elem in self._box:
            if( [elem[0],elem[1]] not in goal):
                return False

        return True

def CountSteps2( map, state):

    i=1

    lst =  [[state._player[0],state._player[1]]]

    while( len(lst) ):

        next_lst = []

        #print("step:", i)

        for elem in lst:

            #print("elem:", elem)

            x = elem[0]
            y = elem[1]

            if( map[x-1][y]==0):    #UP
                map[x-1][y] = i
                next_lst.append([x-1,y])
            if( map[x+1][y]==0):    #DOWN
                map[x+1][y] = i
                next_lst.append([x+1,y])
            if( map[x][y-1]==0):    #LEFT
                map[x][y-1] = i
                next_lst.append([x,y-1])
            if( map[x][y+1]==0):    #RIGHT
                map[x][y+1] = i
                next_lst.append([x,y+1])

        lst = next_lst

        #print( lst)

        i=i+1

        pass

    #set map[i][j]==0 to -9
    for i in range(0,MAP_ROW):
        for j in range(0,MAP_COL):
            if( map[i][j]==0):
                map[i][j]= -9

    map[state._player[0]][state._player[1]] = 0

    pass

#  0: BLANK
# -1: WALL
# -2: BOX
# -3: PLAYER
def CountSteps( map, state):

    #print( state.get_hexdigest())

    #map2 = map.copy()

    # Add BOX, PLAYER to map
    for val in state._box:
        map[val[0]][val[1]]= -2

    map[state._player[0]][state._player[1]] = -3

    #print( map)
    CountSteps2( map, state)

    pass

def SetEligibleMoves( map, state, moves):
    
    i=0

    for elem in state._box:
        x = elem[0]
        y = elem[1]

        if( map[x-1][y]>=0 and map[x+1][y]>=0 ):    #UP/DOWN
            if( isNotForbidden([x-1,y])):
                moves.append([[x+1,y],[-1,0],map[x+1][y], i])
            if( isNotForbidden([x+1,y])):
                moves.append([[x-1,y],[1,0],map[x-1][y], i])

        if( map[x][y-1]>=0 and map[x][y+1]>=0):    #LEFT/RIGHT
            if( isNotForbidden([x,y-1])):
                moves.append([[x,y+1],[0,-1],map[x][y+1], i])
            if( isNotForbidden([x,y+1])):
                moves.append([[x,y-1],[0,1],map[x][y-1], i])

        if( map[x-1][y]==-9 and map[x+1][y]>=0 ):    #UP
            if( isNotForbidden([x-1,y])):
                moves.append([[x+1,y],[-1,0],map[x+1][y], i])

        if( map[x-1][y]>=0 and map[x+1][y]==-9 ):    #DOWN
            if( isNotForbidden([x+1,y])):
                moves.append([[x-1,y],[1,0],map[x-1][y], i])

        if( map[x][y-1]==-9 and map[x][y+1]>=0):    #LEFT
            if( isNotForbidden([x,y-1])):
                moves.append([[x,y+1],[0,-1],map[x][y+1], i])

        if( map[x][y-1]>=0 and map[x][y+1]==-9):    #RIGHT
            if( isNotForbidden([x,y+1])):
                moves.append([[x,y-1],[0,1],map[x][y-1], i])

        i=i+1

    pass


def Solve( state, goal):

    # map : WALLS ONLY
    map = np.zeros((MAP_ROW, MAP_COL),dtype='b')

    for val in state._wall:
        map[val[0]][val[1]]= -1

    trace = {}
    log = []

    if( not Solve2( map, state, goal, 0, 0, trace, log)):
        print( "Cannot Solve!")


def Solve2( map, state, goal, depth, total_steps, trace, log):

    if( total_steps> MAX_STEPS or depth> MAX_DEPTH):
        #print( "total_steps:", total_steps, " depth:", depth)
        return False

    # map2 : WALLS plus STEP COUNT
    map2 = map.copy()

    #Count steps to reachable blank squares
    CountSteps( map2, state)

    #print( map2)

    #Remove illegible moves for the BOX
    moves=[]  # list of [ targetPlayerPosition, moveDirection, steps, box no]
    SetEligibleMoves( map2, state, moves)

    #print( "DEPTH: {} MOVES: {} - {}".format( depth, len(moves), moves))

    str_space = " Move Box: {:d} Steps: {:d} Dir: {}"

    #Try each possible move
    for mov in moves:
        steps = mov[2]
        box_no = mov[3]
        mov_dir = mov[1]

        new_state = copy.deepcopy(state)

        #print( new_state.get_hexdigest())

        str_log = str_space.format( box_no, steps, mov_dir)

        #print( str_log)

        new_state.moveBox( box_no, mov_dir)

        #check if meet goal
        if( new_state.matchGoal(goal)):
            print( "Reach Goals!")
            print( "Depth:", depth+1)
            print( "Total Steps:", total_steps+steps+1)
    
            log.append( str_log)

            for trc_log in log:
                print( trc_log)
            return True

        #check if new_state is duplicate
        
        key = new_state.get_hexdigest()

        if( key in trace):
            #print( "duplicate state!")
            global g_para_duplicate_state_count
            global g_para_duplicate_state_count2

            g_para_duplicate_state_count += 1

            if( trace[key] < depth+1):
                g_para_duplicate_state_count2 += 1
                continue

        log.append( str_log)
        trace[key] = depth+1

        #print( new_state.get_hexdigest())

        #start a new node for search
        if( Solve2( map, new_state, goal, depth+1, total_steps+steps+1, trace, log)):
            return True
            #log.pop()
            #continue    #Find next alternative solution
        else:
            log.pop()
            #trace.pop(key)
        continue

    return False

s = STATE()

mapstr = "#---WWWW-"+"#WWWW PW-"+"#W   B W-"+"#W B   WW"+"#WWB B  W"+"#-W  B  W"+"#-W  WWWW"+"#-WWWW---"

goal = [[3,3],[3,4],[3,5],[4,4],[4,5]]

#goal = [[3,4],[3,2],[4,2],[4,4],[5,4]]  # one step

#goal = [[2,5],[3,2],[4,2],[4,4],[5,4]]  # one step

#goal = [[3,5],[3,2],[4,2],[4,4],[5,4]]  # two steps

goal = [[3,5],[3,2],[4,2],[4,4],[5,3]]  # two steps

goal = [[3,5],[3,3],[4,2],[4,4],[5,3]]  # two steps

goal = [[3,4],[3,3],[4,2],[4,4],[5,5]]  # two steps

goal = [[3,4],[3,3],[4,2],[4,3],[5,5]]  # two steps

goal = [[3,4],[3,3],[3,2],[4,3],[5,5]]  # two steps

MAX_STEPS = 28
MAX_DEPTH = 6
goal = [[3,4],[3,3],[2,2],[4,3],[5,5]]

MAX_STEPS = 32
MAX_DEPTH = 9
goal = [[3,4],[3,3],[2,5],[4,3],[5,5]]

s.setup( mapstr)

start_time = datetime.datetime.now()

Solve( s, goal)

diff_time = datetime.datetime.now() - start_time

print( "Time Diff:{}".format(diff_time))
print( "Duplicate Key Count :{}".format(g_para_duplicate_state_count))
print( "Duplicate Key Count2:{}".format(g_para_duplicate_state_count2))
# Setup Map and State:{ Goal, Box, Player, Wall }

