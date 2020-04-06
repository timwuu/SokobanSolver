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
        
        print( player)
        print( wall)
        print( box)

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
    


def Solve( state, goal):

    pass 

s = STATE()

mapstr = "#---WWWW-"+"#WWWW PW-"+"#W   B W-"+"#W B   WW"+"#WWB B  W"+"#-W  B  W"+"#-W  WWWW"+"#-WWWW---"

goal = [[3,3],[3,4],[3,5],[4,4],[4,5]]

s.setup( mapstr)

Solve( s, goal)

m = hashlib.sha256()

lst = [[0,1],[2,3]]

map = np.array( lst, dtype='b')

m.update( map.tobytes())

print( m.hexdigest())

print( map[0][1])


# Setup Map and State:{ Goal, Box, Player, Wall }

