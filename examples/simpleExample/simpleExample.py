import random
import json
import time
import matplotlib.pyplot as plt
import math
import os
import sys
import datetime
import numpy

import matplotlib.pyplot as plt
from numpy import array
import matplotlib.collections as collections

sys.path.insert(1,'/home/samgomes/Documents/doutoramento/reps/GIMME/GIMME')
sys.path.insert(1,'/GIMME')
sys.path.insert(1,'../')
from GIMMECore import *
from ModelMocks import *


print("------------------------------------------")
print("-----                                -----")
print("-----     SIMPLE GIMME API TEST      -----")
print("-----                                -----")
print("------------------------------------------")

numPlayers = int(input("How many players would you like? "))
numTasks = int(input("How many tasks would you like? "))
adaptationGIMME = Adaptation() 

players = [0 for x in range(numPlayers)]
tasks = [0 for x in range(numTasks)]


preferredNumberOfPlayersPerGroup = int(input("How many players per group would you prefer? "))

playerBridge = CustomPlayerModelBridge(players)
taskBridge = CustomTaskModelBridge(tasks)

profileTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0})


print("Setting up the players...")

for x in range(numPlayers):
	playerBridge.registerNewPlayer(
		playerId = int(x), 
		name = "name", 
		currState = PlayerState(profile = profileTemplate.generateCopy().reset()), 
		pastModelIncreasesGrid = PlayerStateGrid(
			interactionsProfileTemplate = profileTemplate.generateCopy().reset(), 
			gridTrimAlg = QualitySortGridTrimAlg(
				maxNumModelElements = 30, 
				qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
				), 
			numCells = 1
			), 
		currModelIncreases = PlayerCharacteristics(), 
		personalityEst = profileTemplate.generateCopy().reset(), 
		realPersonality = profileTemplate.generateCopy().reset())
	playerBridge.resetState(x)
	playerBridge.getPlayerStateGrid(x).gridTrimAlg.considerStateResidue(True)

print("Setting up the players...")

for x in range(numTasks):
	taskBridge.registerNewTask(
		taskId = int(x), 
		description = "description", 
		minRequiredAbility = random.uniform(0, 1), 
		profile = profileTemplate.generateCopy(), 
		minDuration = datetime.timedelta(minutes=1), 
		difficultyWeight = 0.5, 
		profileWeight = 0.5)

print("Setting up a random group. org. algorithms...")

randomConfigsAlg = RandomConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = profileTemplate.generateCopy(), 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup
)
adaptationGIMME.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = randomConfigsAlg, 
	name="Test Adaptation"
)


ready = True
while(True):
	readyText = ""
	readyText = str(input("Ready to compute iteration (y/n)? "))
	while(readyText!="y" and readyText!="n"):
		readyText = str(input("Please answer y/n: "))
	ready = (readyText=="y")
	if(not ready):
		break


	print("----------------------")
	print("Iteration Summary:\n\n\n")
	print(adaptationGIMME.iterate())

	print("----------------------\n\n\n")
	print("Player States:\n\n\n")
	for x in range(numPlayers):
		print(json.dumps(playerBridge.getPlayerCurrState(x), default=lambda o: o.__dict__, sort_keys=True))


	print("~~~~~~~~~~~~~~~~~~~~~\n\n\n")
