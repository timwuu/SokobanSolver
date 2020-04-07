import numpy as np
import hashlib

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

        print( self._player)
        print( self._wall)
        print( self._box)

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
    
def CountSteps( map, state):

    print( state.get_hexdigest())

    map2 = map.copy()

    for val in state._box:
        map2[val[0]][val[1]]= -2

    map2[state._player[0]][state._player[1]] = -3

    print( map2)

    pass

def Solve( state, goal):

    map = np.zeros((8,8),dtype='b')

    for val in state._wall:
        map[val[0]][val[1]]= -1

    CountSteps( map, state)

    pass 

s = STATE()

mapstr = "#---WWWW-"+"#WWWW PW-"+"#W   B W-"+"#W B   WW"+"#WWB B  W"+"#-W  B  W"+"#-W  WWWW"+"#-WWWW---"

goal = [[3,3],[3,4],[3,5],[4,4],[4,5]]

s.setup( mapstr)

Solve( s, goal)

# Setup Map and State:{ Goal, Box, Player, Wall }

