import hashlib
import copy
import datetime
import threading

# Notation: [ROW][COL]
# Note: Add Forbidden Cells to improve the efficiency
#       Check duplicate state in the search tree, keep DEPTH info
#           ?keep DEPTH or STEPS
#       Add Progress Monitoring
#       ?Store Search Nodes for next batch
#       ?Add Heuristic Move
#       ?Multithreading
#       ?Save Node while max steps/depths exceeded
#       ?Search Bi-directional
#       ?Adjust the order of the list of moves (according to previous move)
#       ?Merge trace and trace_moves

# 
#       2020.04.11 Changed Numpy array to list
#       2020.04.11 Improved State Copy
#       2020.04.11 Removed _wall in STATE
#       2020.04.12 Stored Previous Calculated Moves for each STATE
#       2020.04.13 Change STATE._box dimension to STATE._box[2][box_no]

# DEFINE:
# map[][]:

MAP_WALL = -1
MAP_BOX = -2
MAP_PLAYER = -3
MAP_BLANK = -9

MAX_STEP_COUNT_LST_SIZE = 256

# FirstStep+ #5 No.09
MAP_STR = "#---WWWW-"+"#WWWW PW-"+"#W   B W-"+"#W B   WW"+"#WWB B  W"+"#-W  B  W"+"#-W  WWWW"+"#-WWWW---"

# FirstStep+ #5 No.10
# MAP_STR = "#---WWWW-"+"#WWWW PW-"+"#W   B W-"+"#W B   WW"+"#WWB B  W"+"#-W  B  W"+"#-W  WWWW"+"#-WWWW---"

MAX_STEPS = 28  
MAX_DEPTH = 6
MAP_ROW = 8
MAP_COL = 8
FORBIDDEN = ((1,4),(1,5),(2,1),(3,1),(4,6),(5,6),(7,2),(7,3))

FIND_ONLY_ONE = True

PROGRESS_UPDATE_PERIOD = 5.0 #seconds

g_cnt_mov=0

g_para_total_state_searched = 0
g_para_no_further_moves = 0
g_para_max_exceeded = 0
g_para_duplicate_state_count = 0
g_para_duplicate_state_count2 = 0
g_progress = 0.0
g_progress_prv_time = datetime.datetime.now()

g_tm_CountSteps2 = datetime.timedelta(0)

g_para_hexdigest = 0

g_para_tm_start = datetime.datetime.now()
g_para_tm_diff = datetime.timedelta(0)

def isNotForbidden( pos):
    return ( pos not in FORBIDDEN )

def g_tm_start():
    global g_para_tm_start
    g_para_tm_start = datetime.datetime.now()
    
def g_tm_add():
    global g_para_tm_start
    global g_para_tm_diff
    g_para_tm_diff += datetime.datetime.now() - g_para_tm_start

def g_tm_print( func_name):
    global g_para_tm_diff
    print( "Time Diff ({}): {}".format(func_name, g_para_tm_diff))


class STATE:
    
    def __init__( self, s=None):
        self._player=None

        if( s is not None):
            self._box=[]
            for elem in s._box:
                self._box.append( [*elem])

            self._player = [*s._player]  #faster copy
            #self._player = list( s._player)
        else:
            self._box=[[],[]]

    def get_hexdigest( self):
        global g_para_hexdigest
        g_para_hexdigest += 1
        b = bytes(self._player)
        for elem in self._box:
            b += bytes(elem)
        return hash(b)
        
        m = hashlib.sha256()
        m.update( bytes(self._player))
        #TODO: possible different orders for same positions of boxes
        for elem in self._box:
            m.update( bytes(elem))
        return m.hexdigest()
    
    def moveBox( self, box_no, mov_dir):

        self._player[0] = self._box[0][box_no]
        self._player[1] = self._box[1][box_no]

        self._box[0][box_no] += mov_dir[0]
        self._box[1][box_no] += mov_dir[1]
    
    def matchGoal( self, goal):

        #g_tm_start()

        for i, x in enumerate(self._box[0]):
            if( [x,self._box[1][i]] not in goal):
                #g_tm_add()
                return False

        #g_tm_add()

        return True

def setup( map, state, mapstr):

    i=-1
    j=0

    for c in mapstr:
        if( c=='#'):
            i=i+1
            j=0
            continue

        if( c=='P'):
            state._player = [i,j]
            j=j+1
            continue

        if( c=='W'):
            map[i][j]= MAP_WALL
            j=j+1
            continue

        if( c=='B'):
            state._box[0].append(i)
            state._box[1].append(j)
            j=j+1
            continue

        j=j+1

    #print( state._player)
    #print( state._wall)
    #print( state._box)

def CountSteps2( map, state):

    i=1

    lst =  [[state._player[0],state._player[1]]]

    while( len(lst) ):

        next_lst = []

        #print("step:", i)

        for x,y in lst:

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

    pass

def CountSteps( map, state):

    # Add BOX, PLAYER to map
    for i,x in enumerate( state._box[0]):
        map[x][state._box[1][i]]= MAP_BOX

    map[state._player[0]][state._player[1]] = MAP_PLAYER

    global g_tm_CountSteps2

    tm_tmp = datetime.datetime.now()

    CountSteps2( map, state)

    g_tm_CountSteps2 += datetime.datetime.now() - tm_tmp

    pass

def SearchEligibleMoves( map, state, moves, log):

    i= -1
    
    # Try to move the same box first
    if(len(log)):
        i = log[-1][0]  # last moved box_no 
        #lst_mov_dir = log[-1][2]

        x = state._box[0][i]
        y = state._box[1][i]

        _U = map[x-1][y]
        _D = map[x+1][y]
        _L = map[x][y-1]
        _R = map[x][y+1]

        if( _U>=0 and _D>=0 ):    #UP/DOWN
            if( isNotForbidden((x-1,y))):
                moves.append(((-1,0),_D, i))
            if( isNotForbidden((x+1,y))):
                moves.append(((1,0),_U, i))
        else:
            if( _U== MAP_BLANK and _D>=0 ):    #UP
                if( isNotForbidden((x-1,y))):
                    moves.append(((-1,0),_D, i))

            if( _U>=0 and _D== MAP_BLANK ):    #DOWN
                if( isNotForbidden((x+1,y))):
                    moves.append(((1,0),_U, i))

        if( _L>=0 and _R>=0):    #LEFT/RIGHT
            if( isNotForbidden((x,y-1))):
                moves.append(((0,-1),_R, i))
            if( isNotForbidden((x,y+1))):
                moves.append(((0,1),_L, i))
        else:
            if( _L== MAP_BLANK and _R>=0):    #LEFT
                if( isNotForbidden((x,y-1))):
                    moves.append(((0,-1),_R, i))

            if( _L>=0 and _R== MAP_BLANK):    #RIGHT
                if( isNotForbidden((x,y+1))):
                    moves.append(((0,1),_L, i))

    j=i

    for i, x in enumerate( state._box[0]):

        if(j==i):
            continue

        y = state._box[1][i]

        _U = map[x-1][y]
        _D = map[x+1][y]
        _L = map[x][y-1]
        _R = map[x][y+1]

        if( _U>=0 and _D>=0 ):    #UP/DOWN
            if( isNotForbidden((x-1,y))):
                moves.append(((-1,0),_D, i))
            if( isNotForbidden((x+1,y))):
                moves.append(((1,0),_U, i))
        else:
            if( _U== MAP_BLANK and _D>=0 ):    #UP
                if( isNotForbidden((x-1,y))):
                    moves.append(((-1,0),_D, i))

            if( _U>=0 and _D== MAP_BLANK ):    #DOWN
                if( isNotForbidden((x+1,y))):
                    moves.append(((1,0),_U, i))

        if( _L>=0 and _R>=0):    #LEFT/RIGHT
            if( isNotForbidden((x,y-1))):
                moves.append(((0,-1),_R, i))
            if( isNotForbidden((x,y+1))):
                moves.append(((0,1),_L, i))
        else:
            if( _L== MAP_BLANK and _R>=0):    #LEFT
                if( isNotForbidden((x,y-1))):
                    moves.append(((0,-1),_R, i))

            if( _L>=0 and _R== MAP_BLANK):    #RIGHT
                if( isNotForbidden((x,y+1))):
                    moves.append(((0,1),_L, i))

    pass

def Solve( map, state, goal):

    trace = {}
    trace_moves = {}
    log = []

    if( not Solve2( map, state, state.get_hexdigest(), goal, 0, 0, trace, trace_moves, log, 100.0)):
        print( "No More Solutions!")

    global g_para_total_state_searched
    g_para_total_state_searched = len(trace)
    


def Solve2( map, state, state_key, goal, depth, total_steps, trace, trace_moves, log, progress_slot):

    if( total_steps> MAX_STEPS or depth> MAX_DEPTH):
        global g_para_max_exceeded
        g_para_max_exceeded += 1
        output_progress( progress_slot)  # END_NODE
        return False

    if( state_key in trace_moves):
        moves = trace_moves[state_key]
    else:
        # map2 : WALLS plus STEP COUNT
        #g_tm_start()
        map2=[]
        for elem in map:
            map2.append([*elem])  #2020.04.11 timijk: avoid map2 = copy.deepcopy(map)
        #g_tm_add()

        #Count steps to reachable blank squares
        CountSteps( map2, state)

        #Remove illegible moves for the BOX
        moves=[]  # list of [ targetPlayerPosition, moveDirection, steps, box no]

        #g_tm_start()
        SearchEligibleMoves( map2, state, moves, log)

        trace_moves[state_key] = moves

    if( len(moves)):
        mv_progress_slot = progress_slot/len(moves)
    else:
        global g_para_no_further_moves
        g_para_no_further_moves += 1
        output_progress( progress_slot)  # END_NODE
    #g_tm_add()

    #Try each possible move
    for i_mov, mov in enumerate(moves):

        #if( depth<2): print( depth, mov, mv_progress_slot)
        
        steps = mov[1]
        box_no = mov[2]
        mov_dir = mov[0]

        #g_tm_start()
        new_state = STATE( state) #2020.04.11 timijk: avoid copy.deepcopy(state)
        #g_tm_add()

        new_state.moveBox( box_no, mov_dir)

        g_tm_start()
        key = new_state.get_hexdigest()
        g_tm_add()

        #check if new_state is duplicate

        if( key in trace):
            #print( "duplicate state!")
            global g_para_duplicate_state_count
            global g_para_duplicate_state_count2

            g_para_duplicate_state_count += 1

            if( trace[key] < total_steps+steps+1): #depth+1):
                g_para_duplicate_state_count2 += 1
                output_progress( mv_progress_slot)  # END_NODE
                continue

        log.append([box_no, steps, mov_dir, i_mov])

        trace[key] = total_steps+steps+1  #depth+1

        #check if meet goal
        if( new_state.matchGoal(goal)):
            print( "Reach Goals!")
            print( "Depth:", depth+1)
            print( "Total Steps:", total_steps+steps+1)
    
            for l in log:
                print( " Move Box: {0:2d}   Steps: {1:2d}   Dir: ({2[0]:2d},{2[1]:2d})  i: {3}".format(l[0],l[1],l[2],l[3]))

            if FIND_ONLY_ONE:
                return True

        else:
            #start a new node for search
            if( Solve2( map, new_state, key, goal, depth+1, total_steps+steps+1, trace, trace_moves, log, mv_progress_slot)):
                if FIND_ONLY_ONE:
                    return True

        log.pop()   #Find next solution

        continue

    return False

def output_progress( progress):
    global g_progress
    global g_progress_prv_time

    g_progress += progress
    
    tmp = datetime.datetime.now()

    if( tmp - g_progress_prv_time > datetime.timedelta(seconds=PROGRESS_UPDATE_PERIOD)):
        print( "progress: {:.4f}%".format(g_progress))
        g_progress_prv_time = tmp

s = STATE()

goal = [[3,3],[3,4],[3,5],[4,4],[4,5]]

#goal = [[3,4],[3,2],[4,2],[4,4],[5,4]]  # one step

MAX_STEPS = 21
MAX_DEPTH = 4
goal = [[2,5],[3,2],[4,2],[4,4],[5,4]]  # one step

# goal = [[3,5],[3,2],[4,2],[4,4],[5,4]]  # two steps

# goal = [[3,5],[3,2],[4,2],[4,4],[5,3]]  # two steps

# MAX_STEPS = 21
# MAX_DEPTH = 4
# goal = [[3,5],[3,3],[4,2],[4,4],[5,3]]  # two steps

# goal = [[3,4],[3,3],[4,2],[4,4],[5,5]]  # two steps

# goal = [[3,4],[3,3],[4,2],[4,3],[5,5]]  # two steps

# goal = [[3,4],[3,3],[3,2],[4,3],[5,5]]  # two steps

# # Time Used:0:00:01.915810
MAX_STEPS = 27
MAX_DEPTH = 6
goal = [[3,4],[3,3],[2,2],[4,3],[5,5]]

# Time Used: 0:00:04.376139
# Time Used (g_tm_CountSteps2): 0:00:00.389023
# Total State Key Calced: 175582
# Total State Searched: 18628
# Total Max Exceeded: 111053
# Duplicate Key Count : 156954
# Duplicate Key Count2: 26714
MAX_STEPS = 40 #31
MAX_DEPTH = 10 #8
goal = [[3,4],[3,3],[2,4],[4,3],[5,5]]

# Time Used: 0:00:46.802952
# Time Used (g_tm_CountSteps2): 0:00:15.552429

# Time Used: 0:00:49.079644
# Time Used (g_tm_CountSteps2): 0:00:01.171708
# Total State Key Calced: 459538
# Total State Searched: 33324
# Total Max Exceeded: 276172
# Duplicate Key Count : 426214
# Duplicate Key Count2: 79402
# MAX_STEPS = 32
# MAX_DEPTH = 9
# goal = [[3,4],[3,3],[2,5],[4,3],[5,5]]

# OLD
# Time Used: 0:01:44.899962
# Time Used (g_tm_CountSteps2): 0:00:34.329142

# OLD
# Time Used: 0:01:42.817481
# Time Used (g_tm_CountSteps2): 0:00:02.547291

# IMPROVED STATE COPY
# Time Used: 0:00:12.847308
# Time Used (g_tm_CountSteps2): 0:00:02.490403
# Total State Key Calced: 994934
# Total No Further Moves: 9089
# Total State Searched: 53777
# Total Max Exceeded: 553840
# Duplicate Key Count : 941157
# Duplicate Key Count2: 202331
# Time Diff (STATE Copy): 0:00:05.010297
# Time Diff (Match Goal): 0:00:00.849648
# Time Diff (Map Copy): 0:00:00.340164
# Time Diff (Search Moves): 0:00:01.679781
# Time Diff (get_hexdigest): 0:00:03.941602
# Time Diff (get_hexdigest): 0:00:02.270690 using hash()
if FIND_ONLY_ONE:
    MAX_STEPS = 33
    MAX_DEPTH = 10
else:
    MAX_STEPS = 40
    MAX_DEPTH = 5
goal = [[4,4],[3,3],[2,5],[4,3],[5,5]]

# [Key with STEPS] (trace_moves)
# Time Used: 0:00:22.840702
# Time Used (g_tm_CountSteps2): 0:00:01.363490
# Total State Key Calced: 2928439
# Total No Further Moves: 16802
# Total State Searched: 182459
# Total Max Exceeded: 597015
# Duplicate Key Count : 2745979
# Duplicate Key Count2: 1692313
# Time Diff (get_hexdigest): 0:00:06.745612
if FIND_ONLY_ONE:
    MAX_STEPS = 40
    MAX_DEPTH = 13
else:
    MAX_STEPS = 50
    MAX_DEPTH = 15
goal = [[4,4],[3,3],[2,5],[4,3],[5,2]]

# Time Used: 0:01:46.088441
# Time Used (g_tm_CountSteps2): 0:00:22.916681
# Total State Key Calced: 9359991
# Total No Further Moves: 57642
# Total State Searched: 333013
# Total Max Exceeded: 1250954
# Duplicate Key Count : 9026978
# Duplicate Key Count2: 6053510
# Time Diff (get_hexdigest): 0:00:20.897036
# MAX_STEPS = 45
# MAX_DEPTH = 16
# goal = [[4,4],[3,3],[2,5],[4,3],[2,2]]

# # Time Used:
# MAX_STEPS = 46
# MAX_DEPTH = 17
# goal = [[4,4],[3,4],[2,5],[4,3],[2,2]]

# Time Used: 0:04:31.386291
# Time Used (g_tm_CountSteps2): 0:00:57.143842
# Total State Key Calced: 24114280
# Total No Further Moves: 163471
# Total State Searched: 548603
# Total Max Exceeded: 2344236
# Duplicate Key Count : 23565677
# Duplicate Key Count2: 16472340
# Time Diff (get_hexdigest): 0:00:53.870424
# MAX_STEPS = 52
# MAX_DEPTH = 19
# goal = [[4,4],[3,4],[4,5],[4,3],[2,2]]

# Time Used: 0:09:37.125761
# Time Used (g_tm_CountSteps2): 0:01:59.701923
# Total State Key Calced: 50147734
# Total No Further Moves: 300190
# Total State Searched: 796703
# Total Max Exceeded: 4040017
# Duplicate Key Count : 49351031
# Duplicate Key Count2: 35261005
# Time Diff (get_hexdigest): 0:01:55.930455
# MAX_STEPS = 61
# MAX_DEPTH = 20
# goal = [[4,4],[3,4],[4,5],[3,3],[2,2]]

# STEPS: 73 [trace_moves]
# Time Used: 0:13:24.848147
# Time Used (g_tm_CountSteps2): 0:00:11.611889
# Total State Key Calced: 117129648
# Total No Further Moves: 749693
# Total State Searched: 1135304
# Total Max Exceeded: 6397163
# Duplicate Key Count : 115994343
# Duplicate Key Count2: 85313455
# Time Diff (get_hexdigest): 0:04:19.576780
# MAX_STEPS = 71
# MAX_DEPTH = 24
# goal = [[4,4],[3,4],[4,5],[3,3],[3,5]]


# MAX_STEPS = 34
# MAX_DEPTH = 10
# goal = [[3,2],[3,3],[3,4],[3,5],[4,3]]


map = [[MAP_BLANK for i in range(MAP_COL)] for j in range(MAP_ROW)]

setup( map, s, MAP_STR)

g_progress_prv_time = datetime.datetime.now()

start_time = datetime.datetime.now()

if True:
    Solve( map, s, goal)
else:
    x = threading.Thread( target=Solve, args=(map,s,goal))
    x.start()
    x.join()

diff_time = datetime.datetime.now() - start_time

print( "Time Used: {}".format(diff_time))
print( "Time Used (g_tm_CountSteps2): {}".format(g_tm_CountSteps2))

print( "Total State Key Calced: {}".format(g_para_hexdigest))
print( "Total No Further Moves: {}".format(g_para_no_further_moves))
print( "Total State Searched: {}".format(g_para_total_state_searched))
print( "Total Max Exceeded: {}".format(g_para_max_exceeded))
print( "Duplicate Key Count : {}".format(g_para_duplicate_state_count))
print( "Duplicate Key Count2: {}".format(g_para_duplicate_state_count2))

g_tm_print("get_hexdigest")

# Setup Map and State:{ Goal, Box, Player, Wall }

