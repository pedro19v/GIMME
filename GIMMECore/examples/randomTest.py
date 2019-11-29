import random
import json
import copy
import time
import matplotlib.pyplot as plt
import math
import datetime
import os
import sys
sys.path.append(os.path.join(sys.path[0],'..'))

from GIMMECore import *
from ModelMocks import *



random.seed(time.perf_counter())

numRuns = 10000
# random.uniform(0.0, 1.0)



values=[ ((random.uniform(0.0, 1.0) - random.uniform(0.0, 1.0))**2+(random.uniform(0.0, 1.0) - random.uniform(0.0, 1.0))**2)**1/2 for i in range(numRuns)]
timesteps=[i for i in range(numRuns)]


# -------------------------------------------------------
plt.scatter(timesteps, values, label=r'$GIMME\ strategy$', s=1)

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")
plt.legend(loc='best')

plt.show()
