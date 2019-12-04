import numpy
import random
import json
import os
import sys
import datetime

sys.path.append(os.path.join(sys.path[0],'..'))
from ModelMocks import *

numPlayers = 10

players = [None for x in range(numPlayers)]
tasks = [None for x in range(20)]

playerBridge = CustomPlayerModelBridge(players)
taskBridge = CustomTaskModelBridge(tasks)

for x in range(numPlayers):
	playerBridge.registerNewPlayer(int(x), "name", PlayerState(time.time()), PlayerStateGrid(numCells = 1, maxProfilesPerCell = 30), PlayerCharacteristics(), InteractionsProfile())
for x in range(20):
	taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), datetime.timedelta(minutes=1), 0.5, 0.5)

regressionAlg = KNNRegression(playerBridge, 5)
print(regressionAlg.predict(InteractionsProfile(0.2,0.5,0.6,0.2), 5))
