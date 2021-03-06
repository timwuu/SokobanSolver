import numpy as np
import hashlib
import datetime

MAX_STEP_COUNT_LST_SIZE= 256

g_lst_1 = np.empty((MAX_STEP_COUNT_LST_SIZE, 2),dtype='i4')
g_lst_2 = np.empty((MAX_STEP_COUNT_LST_SIZE, 2),dtype='i4')
        

g_lst_3 = np.empty((MAX_STEP_COUNT_LST_SIZE*2),dtype='u2')
g_lst_4 = np.empty((MAX_STEP_COUNT_LST_SIZE*2),dtype='u2')

def Loop():


    lst_a, lst_b = g_lst_3, g_lst_4    

    a=3
    b=4

    len=0

    x,y=4,6

    player=[2,3]
    
    box = [[3,3],[3,4],[3,5],[4,4],[4,5]]

    npbox = np.array( box, dtype='b')

    for i in range(0,10000):
        for k in range(0,MAX_STEP_COUNT_LST_SIZE):
            m = hashlib.sha256()
            m.update( bytes(player))
            m.update( npbox.tobytes())
            m.hexdigest()

    pass


start_time = datetime.datetime.now()

Loop()

diff_time = datetime.datetime.now() - start_time

print( "Time Used: {}".format(diff_time))



# 2.8~2,9 per 10,000^2
# a,b = b,a
# lst_a, lst_b = lst_b, lst_a

# 'u2' np.array
# 1.6~1.7 per 10,000*256
# lst_a[k]=[x-1,y]
# k += 1


# 0.26~0.28 per 10,000*256
# lst_a.append([x-1,y])

# 0.18~0.19 per 10,000*256
# lst_a[k]=[x-1,y]

# 0.43~0.47 per 10,000*256
# lst_a[k],lst_b[k]=x-1,y

# 6.66 per 10,000*256
#             m = hashlib.sha256()
#             m.update( bytes(player))
#             for elem in box:
#                 m.update( bytes(elem))
#             m.hexdigest()

# 3.6 per 10,000*256
            # m = hashlib.sha256()
            # m.update( bytes(player))
            # m.update( npbox.tobytes())
            # m.hexdigest()