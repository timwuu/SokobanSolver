import numpy as np
import hashlib
import copy
import datetime
import threading

# Notation: [ROW][COL]
# Note: Add Forbidden Cells to improve the efficiency
#       Check duplicate state in the search tree, keep DEPTH info
#       Add Progress Monitoring
#       ?Store Search Nodes for next batch
#       ?Add Heuristic Move
#       ?Multithreading
#       ?Save Node while max steps/depths exceeded

# DEFINE:
# map[][]:
# -1: WALL
# -2: BOX
# -3: PLAYER
# -9: BLANK

MAP_BLANK = -9

MAX_STEPS = 28  
MAX_DEPTH = 6
MAP_ROW = 8
MAP_COL = 8
FORBIDDEN = [[1,4],[1,5],[2,1],[3,1],[4,6],[5,6],[7,2],[7,3]]

g_para_total_state_searched = 0
g_para_max_exceeded = 0
g_para_duplicate_state_count = 0
g_para_duplicate_state_count2 = 0
g_progress = 0.0
g_progress_prv_time = datetime.datetime.now()

g_tm_CountSteps2 = datetime.timedelta(0)

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

    global g_tm_CountSteps2

    tm_tmp = datetime.datetime.now()

    i=1

    lst =  [[state._player[0],state._player[1]]]

    while( len(lst) ):

        next_lst = []

        #print("step:", i)

        for elem in lst:

            #print("elem:", elem)

            x = elem[0]
            y = elem[1]

            if( map[x-1][y]== MAP_BLANK):    #UP
                map[x-1][y] = i
                next_lst.append([x-1,y])
            if( map[x+1][y]== MAP_BLANK):    #DOWN
                map[x+1][y] = i
                next_lst.append([x+1,y])
            if( map[x][y-1]== MAP_BLANK):    #LEFT
                map[x][y-1] = i
                next_lst.append([x,y-1])
            if( map[x][y+1]== MAP_BLANK):    #RIGHT
                map[x][y+1] = i
                next_lst.append([x,y+1])

        lst = next_lst

        #print( lst)

        i=i+1

        pass

    map[state._player[0]][state._player[1]] = 0

    g_tm_CountSteps2 += datetime.datetime.now() - tm_tmp

    pass

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

def SearchEligibleMoves( map, state, moves, log):

    i= -1
    
    # Try to move the same box first
    if(len(log)):
        i = log[-1][0]  # last moved box_no 
        #lst_mov_dir = log[-1][2]

        elem = state._box[i]

        x = elem[0]
        y = elem[1]

        _U = map[x-1][y]
        _D = map[x+1][y]
        _L = map[x][y-1]
        _R = map[x][y+1]

        if( _U>=0 and _D>=0 ):    #UP/DOWN
            if( isNotForbidden([x-1,y])):
                moves.append([[x+1,y],[-1,0],_D, i])
            if( isNotForbidden([x+1,y])):
                moves.append([[x-1,y],[1,0],_U, i])
        else:
            if( _U== MAP_BLANK and _D>=0 ):    #UP
                if( isNotForbidden([x-1,y])):
                    moves.append([[x+1,y],[-1,0],_D, i])

            if( _U>=0 and _D== MAP_BLANK ):    #DOWN
                if( isNotForbidden([x+1,y])):
                    moves.append([[x-1,y],[1,0],_U, i])

        if( _L>=0 and _R>=0):    #LEFT/RIGHT
            if( isNotForbidden([x,y-1])):
                moves.append([[x,y+1],[0,-1],_R, i])
            if( isNotForbidden([x,y+1])):
                moves.append([[x,y-1],[0,1],_L, i])
        else:
            if( _L== MAP_BLANK and _R>=0):    #LEFT
                if( isNotForbidden([x,y-1])):
                    moves.append([[x,y+1],[0,-1],_R, i])

            if( _L>=0 and _R== MAP_BLANK):    #RIGHT
                if( isNotForbidden([x,y+1])):
                    moves.append([[x,y-1],[0,1],_L, i])

    j=i

    for i, elem in enumerate( state._box):

        if(j==i):
            continue

        x = elem[0]
        y = elem[1]

        _U = map[x-1][y]
        _D = map[x+1][y]
        _L = map[x][y-1]
        _R = map[x][y+1]

        if( _U>=0 and _D>=0 ):    #UP/DOWN
            if( isNotForbidden([x-1,y])):
                moves.append([[x+1,y],[-1,0],_D, i])
            if( isNotForbidden([x+1,y])):
                moves.append([[x-1,y],[1,0],_U, i])
        else:
            if( _U== MAP_BLANK and _D>=0 ):    #UP
                if( isNotForbidden([x-1,y])):
                    moves.append([[x+1,y],[-1,0],_D, i])

            if( _U>=0 and _D== MAP_BLANK ):    #DOWN
                if( isNotForbidden([x+1,y])):
                    moves.append([[x-1,y],[1,0],_U, i])

        if( _L>=0 and _R>=0):    #LEFT/RIGHT
            if( isNotForbidden([x,y-1])):
                moves.append([[x,y+1],[0,-1],_R, i])
            if( isNotForbidden([x,y+1])):
                moves.append([[x,y-1],[0,1],_L, i])
        else:
            if( _L== MAP_BLANK and _R>=0):    #LEFT
                if( isNotForbidden([x,y-1])):
                    moves.append([[x,y+1],[0,-1],_R, i])

            if( _L>=0 and _R== MAP_BLANK):    #RIGHT
                if( isNotForbidden([x,y+1])):
                    moves.append([[x,y-1],[0,1],_L, i])

    pass

def Solve( state, goal):

    # map : WALLS ONLY
    # map = np.zeros((MAP_ROW, MAP_COL),dtype='b')
    map = np.full((MAP_ROW, MAP_COL), fill_value=MAP_BLANK, dtype='b')

    for val in state._wall:
        map[val[0]][val[1]]= -1

    trace = {}
    log = []

    if( not Solve2( map, state, goal, 0, 0, trace, log, 100.0)):
        print( "Cannot Solve!")

    global g_para_total_state_searched
    g_para_total_state_searched = len(trace)
    


def Solve2( map, state, goal, depth, total_steps, trace, log, progress_slot):

    if( total_steps> MAX_STEPS or depth> MAX_DEPTH):
        global g_para_max_exceeded
        g_para_max_exceeded += 1
        output_progress( progress_slot)  # END_NODE
        return False

    # map2 : WALLS plus STEP COUNT
    map2 = map.copy()

    #Count steps to reachable blank squares
    CountSteps( map2, state)

    #print( map2)

    #Remove illegible moves for the BOX
    moves=[]  # list of [ targetPlayerPosition, moveDirection, steps, box no]
    SearchEligibleMoves( map2, state, moves, log)

    if( len(moves)):
        mv_progress_slot = progress_slot/len(moves)
    else:
        output_progress( progress_slot)  # END_NODE

    #Try each possible move
    for i_mov, mov in enumerate(moves):

        #if( depth<2): print( depth, mov, mv_progress_slot)
        
        steps = mov[2]
        box_no = mov[3]
        mov_dir = mov[1]

        new_state = copy.deepcopy(state)

        #print( new_state.get_hexdigest())

        #print( str_log)

        new_state.moveBox( box_no, mov_dir)

        #check if meet goal
        if( new_state.matchGoal(goal)):
            print( "Reach Goals!")
            print( "Depth:", depth+1)
            print( "Total Steps:", total_steps+steps+1)
    
            log.append([box_no, steps, mov_dir, i_mov])

            for l in log:
                print( " Move Box: {:d} Steps: {:d} Dir: {} i: {}".format(l[0],l[1],l[2],l[3]))
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
                output_progress( mv_progress_slot)  # END_NODE
                continue

        log.append([box_no, steps, mov_dir, i_mov])
        trace[key] = depth+1

        #print( new_state.get_hexdigest())

        #start a new node for search
        if( Solve2( map, new_state, goal, depth+1, total_steps+steps+1, trace, log, mv_progress_slot)):
            return True
            #log.pop()
            #continue    #Find next alternative solution
        else:
            log.pop()            
            #output_progress( mv_progress_slot)
            #trace.pop(key)
        continue

    return False

def output_progress( progress):
    global g_progress
    global g_progress_prv_time

    g_progress += progress
    
    tmp = datetime.datetime.now()

    if( tmp - g_progress_prv_time > datetime.timedelta(seconds=2.0)):
        print( "progress: {:.4f}%".format(g_progress))
        g_progress_prv_time = tmp

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

# Time Used:0:00:01.915810
MAX_STEPS = 28
MAX_DEPTH = 6
goal = [[3,4],[3,3],[2,2],[4,3],[5,5]]

# Time Used:0:01:04.020900
MAX_STEPS = 32
MAX_DEPTH = 9
goal = [[3,4],[3,3],[2,5],[4,3],[5,5]]

# # Time Used:0:03:30.385308
# MAX_STEPS = 33
# MAX_DEPTH = 10
# goal = [[4,4],[3,3],[2,5],[4,3],[5,5]]

# # Time Used:0:29:37.108837
# MAX_STEPS = 40
# MAX_DEPTH = 13
# goal = [[4,4],[3,3],[2,5],[4,3],[5,2]]

# # Time Used:
# MAX_STEPS = 45
# MAX_DEPTH = 16
# goal = [[4,4],[3,3],[2,5],[4,3],[2,2]]

# # Time Used:
# MAX_STEPS = 46
# MAX_DEPTH = 17
# goal = [[4,4],[3,4],[2,5],[4,3],[2,2]]

# # Time Used:
# MAX_STEPS = 52
# MAX_DEPTH = 19
# goal = [[4,4],[3,4],[4,5],[4,3],[2,2]]

# # Time Used:
# MAX_STEPS = 61
# MAX_DEPTH = 20
# goal = [[4,4],[3,4],[4,5],[3,3],[2,2]]

# # Time Used:
# MAX_STEPS = 71
# MAX_DEPTH = 24
# goal = [[4,4],[3,4],[4,5],[3,3],[3,5]]

s.setup( mapstr)

x = threading.Thread( target=Solve, args=(s,goal))

g_progress_prv_time = datetime.datetime.now()

start_time = datetime.datetime.now()

x.start()

#Solve( s, goal)

x.join()

diff_time = datetime.datetime.now() - start_time

print( "Time Used: {}".format(diff_time))
print( "Time Used (g_tm_CountSteps2): {}".format(g_tm_CountSteps2))

print( "Total State Searched: {}".format(g_para_total_state_searched))
print( "Total Max Exceeded: {}".format(g_para_max_exceeded))
print( "Duplicate Key Count : {}".format(g_para_duplicate_state_count))
print( "Duplicate Key Count2: {}".format(g_para_duplicate_state_count2))

# Setup Map and State:{ Goal, Box, Player, Wall }

# Logs:
# Time Used:0:29:37.108837
# Total State Searched:    184,658
# Duplicate Key Count : 11,319,687
# Duplicate Key Count2:  3,602,166
# MAX_STEPS = 40
# MAX_DEPTH = 13
# goal = [[4,4],[3,3],[2,5],[4,3],[5,2]]

# Depth: 13
# Total Steps: 40
#  Move Box: 0 Steps: 1 Dir: [1, 0] i: 0
#  Move Box: 4 Steps: 4 Dir: [0, 1] i: 6
#  Move Box: 1 Steps: 7 Dir: [0, 1] i: 3
#  Move Box: 3 Steps: 6 Dir: [0, -1] i: 2
#  Move Box: 2 Steps: 3 Dir: [-1, 0] i: 2
#  Move Box: 2 Steps: 0 Dir: [-1, 0] i: 0
#  Move Box: 2 Steps: 2 Dir: [0, 1] i: 0
#  Move Box: 2 Steps: 0 Dir: [0, 1] i: 1
#  Move Box: 2 Steps: 0 Dir: [0, 1] i: 1
#  Move Box: 0 Steps: 0 Dir: [1, 0] i: 2
#  Move Box: 4 Steps: 4 Dir: [0, -1] i: 5
#  Move Box: 4 Steps: 0 Dir: [0, -1] i: 0
#  Move Box: 4 Steps: 0 Dir: [0, -1] i: 0
