import numpy
import random
import json
import copy

import time

import matplotlib.pyplot as plt
import math


from GIMMECore import *
from ModelMocks import *

from numpy import array

import random
random.seed(time.clock())

numRuns = 10
numIterationsPerRun = 50
numTrainingCyclesPerRun = 30

playerWindow = 30

numPlayers = 23

players = [None for x in range(numPlayers)]
tasks = [None for x in range(20)]

class CustomTaskModelBridge(TaskModelBridge):
	
	def registerNewTask(self, taskId, description, minRequiredAbility, profile, difficultyWeight, profileWeight):
		tasks[taskId] = TaskModelMock(taskId, description, minRequiredAbility, profile, difficultyWeight, profileWeight)

	def getSelectedTaskIds(self):
		return [int(i) for i in range(20)]

	def getTaskInteractionsProfile(self, taskId):
		return tasks[taskId].profile

	def getTaskMinRequiredAbility(self, taskId):
		return tasks[taskId].minRequiredAbility

	def getTaskDifficultyWeight(self, taskId):
		return tasks[taskId].difficultyWeight

	def getTaskProfileWeight(self, taskId):
		return tasks[taskId].profileWeight


class CustomPlayerModelBridge(PlayerModelBridge):
	
	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality, numIterationsPerRun):
		players[int(playerId)] = PlayerModelMock(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality, numIterationsPerRun)	

	def resetPlayer(self, playerId):
		print(json.dumps(players[int(playerId)], default=lambda o: o.__dict__, sort_keys=True))
		players[int(playerId)].currState.reset()
		players[int(playerId)].pastModelIncreasesGrid.reset()
		print(json.dumps(players[int(playerId)], default=lambda o: o.__dict__, sort_keys=True))

	def savePlayerState(self, playerId, newState):
		players[int(playerId)].currState = newState
		players[int(playerId)].pastModelIncreasesGrid.pushToGrid(newState)

	def getIterationReactions(self, playerId, currIteration):
		return players[int(playerId)].iterationReactions[currIteration]

	def initIterationReactions(self, playerId, reactions):
		players[int(playerId)].iterationReactions = reactions

	def saveIterationReaction(self, playerId, currIteration, reaction):
		players[int(playerId)].iterationReactions[currIteration] = reaction

	def saveInherentPreference(self, playerId, ip):
		players[int(playerId)].inherentPreference = ip

	def getInherentPreference(self, playerId):
		return players[int(playerId)].inherentPreference

	def saveBaseLearningRate(self, playerId, blr):
		players[int(playerId)].baseLearningRate = blr

	def getBaseLearningRate(self, playerId):
		return players[int(playerId)].baseLearningRate


	def getSelectedPlayerIds(self):
		return [int(i) for i in range(numPlayers)]


	def getPlayerName(self, playerId):
		return players[int(playerId)].name

	def getPlayerCurrState(self,  playerId):
		return players[int(playerId)].currState

	def getPlayerCurrProfile(self,  playerId):
		return players[int(playerId)].currState.profile

	def getPlayerPastModelIncreases(self, playerId):
		return players[int(playerId)].pastModelIncreasesGrid

	def getPlayerCurrCharacteristics(self, playerId):
		return players[int(playerId)].currState.characteristics
	
	def getPlayerPersonality(self, playerId):
		return players[int(playerId)].personality


	def setPlayerPersonality(self, playerId, personality):
		players[int(playerId)].personality = personality

	def setPlayerCharacteristics(self, playerId, characteristics):
		players[int(playerId)].currState.characteristics = characteristics

	def setPlayerCurrProfile(self, playerId, profile):
		players[int(playerId)].currState.profile = profile



def simulateReaction(currIteration, playerBridge, playerId):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(copy.deepcopy(currState), playerBridge, playerId, currState.profile, currIteration)

	newState.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	# print(json.dumps(currState.characteristics, default=lambda o: o.__dict__, sort_keys=True))
	# print(json.dumps(newState.characteristics, default=lambda o: o.__dict__, sort_keys=True))

	playerBridge.savePlayerState(playerId, newState)

def calcReaction(state, playerBridge, playerId, interactionsProfile, currIteration):
	# print(len(playerBridge.getPlayerPastModelIncreases(playerId).cells[0]))
	inherentPreference = playerBridge.getInherentPreference(playerId)
	state.characteristics.engagement = 0.5* (state.characteristics.engagement) + 0.5* (2.0 - inherentPreference.sqrDistanceBetween(interactionsProfile))/2.0

	currTaskReaction = playerBridge.getIterationReactions(playerId, currIteration)
	abilityIncreaseSim = (currTaskReaction * state.characteristics.engagement) #between 0 and 1
	state.characteristics.ability = state.characteristics.ability + abilityIncreaseSim
	
	return state


# create players, tasks and adaptation
playerBridge = CustomPlayerModelBridge()
for x in range(numPlayers):
	playerBridge.registerNewPlayer(int(x), "name", PlayerState(), PlayerStateGrid(1, playerWindow), PlayerCharacteristics(), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), numIterationsPerRun)

# print(json.dumps(players, default=lambda o: o.__dict__, sort_keys=True))

taskBridge = CustomTaskModelBridge()
for x in range(20):
	taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), 0.5, 0.5)

adaptationGIMME = Adaptation()
adaptationGIMME10 = Adaptation()
adaptationGIMME1000 = Adaptation()
adaptationGIMME2000  = Adaptation()
adaptationGIMMEK1 = Adaptation()
adaptationGIMMEK24 = Adaptation()
adaptationGIMMEK30 = Adaptation()



adaptationRandom = Adaptation()
adaptationOptimal = Adaptation()



# init players
for x in range(numPlayers):
	playerBridge.saveInherentPreference(x, InteractionsProfile(K_i=numpy.random.uniform(0, 1), K_cp=numpy.random.uniform(0, 1), K_mh=numpy.random.uniform(0, 1), K_pa=numpy.random.uniform(0, 1)))
	playerBridge.saveBaseLearningRate(x, numpy.random.uniform(0.2, 0.6))
	playerBridge.initIterationReactions(x, [0]*(numTrainingCyclesPerRun + numIterationsPerRun+1))

	for p in range(numTrainingCyclesPerRun + numIterationsPerRun+1):
		playerBridge.saveIterationReaction(x, p, numpy.random.normal(playerBridge.getBaseLearningRate(x), 0.05))




adaptationGIMME10.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=10, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMME.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMME1000.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=1000, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMME2000.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=2000, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMMEK1.init(KNNRegression(1), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)

adaptationGIMMEK24.init(KNNRegression(24), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMMEK30.init(KNNRegression(30), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)



adaptationRandom.init(KNNRegression(5), RandomConfigsGen(), RandomFitness(), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)

simOptimalFitness = SimulationsOptimalFitness(calcReaction, PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates
adaptationOptimal.init(KNNRegression(5), RandomConfigsGen(), simOptimalFitness, playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)


GIMME10Abilities = [0 for i in range(numIterationsPerRun)]
GIMME10Engagements = [0 for i in range(numIterationsPerRun)]
GIMME10PrefProfDiff = [0 for i in range(numIterationsPerRun)]

GIMMEAbilities = [0 for i in range(numIterationsPerRun)]
GIMMEEngagements = [0 for i in range(numIterationsPerRun)]
GIMMEPrefProfDiff = [0 for i in range(numIterationsPerRun)]

GIMME1000Abilities = [0 for i in range(numIterationsPerRun)]
GIMME1000Engagements = [0 for i in range(numIterationsPerRun)]
GIMME1000PrefProfDiff = [0 for i in range(numIterationsPerRun)]

GIMME2000Abilities = [0 for i in range(numIterationsPerRun)]
GIMME2000Engagements = [0 for i in range(numIterationsPerRun)]
GIMME2000PrefProfDiff = [0 for i in range(numIterationsPerRun)]


GIMMEK1Abilities = [0 for i in range(numIterationsPerRun)]
GIMMEK1Engagements = [0 for i in range(numIterationsPerRun)]
GIMMEK1PrefProfDiff = [0 for i in range(numIterationsPerRun)]

GIMMEK24Abilities = [0 for i in range(numIterationsPerRun)]
GIMMEK24Engagements = [0 for i in range(numIterationsPerRun)]
GIMMEK24PrefProfDiff = [0 for i in range(numIterationsPerRun)]

GIMMEK30Abilities = [0 for i in range(numIterationsPerRun)]
GIMMEK30Engagements = [0 for i in range(numIterationsPerRun)]
GIMMEK30PrefProfDiff = [0 for i in range(numIterationsPerRun)]


randomAbilities = [0 for i in range(numIterationsPerRun)]
randomEngagements = [0 for i in range(numIterationsPerRun)]
randomPrefProfDiff = [0 for i in range(numIterationsPerRun)]


optimalAbilities = [0 for i in range(numIterationsPerRun)]
optimalEngagements = [0 for i in range(numIterationsPerRun)]
optimalPrefProfDiff = [0 for i in range(numIterationsPerRun)]



GIMME10ExecTime = 0.0
GIMMEExecTime = 0.0
GIMME1000ExecTime = 0.0
GIMME2000ExecTime = 0.0

GIMMEK1ExecTime = 0.0
GIMMEK24ExecTime = 0.0
GIMMEK30ExecTime = 0.0

randomExecTime = 0.0
optimalExecTime = 0.0

def executeSimulations(adaptation,abilityArray,engagementArray,profDiffArray, avgItExecTime, isOptimalRun, algorithmNum, numAlgorithms):


	for r in range(numRuns):
		for x in range(numPlayers):
			playerBridge.resetPlayer(x)

		# if isOptimalRun == True:
		# 	print(json.dumps(players, default=lambda o: o.__dict__, sort_keys=True))
		# 	quit()

		for i in range(numTrainingCyclesPerRun):
			for x in range(numPlayers):
				simulateReaction(i, playerBridge, x)

		for i in range(numIterationsPerRun):
			if isOptimalRun == True:
				simOptimalFitness.updateCurrIteration(i)

			t0 = time.clock()

			print("step (" +str(i)+ " of "+str(numIterationsPerRun)+") of run ("+str(r)+" of "+str(numRuns)+") of algorithm ("+str(algorithmNum)+" of "+str(numAlgorithms)+")						", end="\r")
			iteration = adaptation.iterate()

			t1 = time.clock() - t0
			avgItExecTime += (t1 - t0)/(numRuns*numIterationsPerRun) # CPU seconds elapsed (floating point)

			for x in range(numPlayers):
				abilityArray[i] += playerBridge.getPlayerCurrCharacteristics(x).ability / (numIterationsPerRun*numRuns)
				engagementArray[i] += playerBridge.getPlayerCurrCharacteristics(x).engagement / (numIterationsPerRun*numRuns)
				profDiffArray[i] += playerBridge.getInherentPreference(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / (numIterationsPerRun*numRuns)
				simulateReaction(i, playerBridge, x)


executeSimulations(adaptationOptimal,optimalAbilities,optimalEngagements,optimalPrefProfDiff, optimalExecTime, True, 9, 9)
executeSimulations(adaptationRandom,randomAbilities,randomEngagements,randomPrefProfDiff, randomExecTime, False, 8, 9)

# executeSimulations(adaptationGIMME10,GIMME10Abilities,GIMME10Engagements,GIMME10PrefProfDiff,GIMME10ExecTime, False, 1, 9)
executeSimulations(adaptationGIMME,GIMMEAbilities,GIMMEEngagements,GIMMEPrefProfDiff,GIMMEExecTime, False, 2, 9)
# executeSimulations(adaptationGIMME1000,GIMME1000Abilities,GIMME1000Engagements,GIMME1000PrefProfDiff,GIMME1000ExecTime, False, 3, 9)
# executeSimulations(adaptationGIMME2000,GIMME2000Abilities,GIMME2000Engagements,GIMME2000PrefProfDiff,GIMME2000ExecTime, False, 4, 9)
# executeSimulations(adaptationGIMMEK1,GIMMEK1Abilities,GIMMEK1Engagements,GIMMEK1PrefProfDiff,GIMMEK1ExecTime, False, 5, 9)
# executeSimulations(adaptationGIMMEK24,GIMMEK24Abilities,GIMMEK24Engagements,GIMMEK24PrefProfDiff,GIMMEK24ExecTime, False, 6, 9)
# executeSimulations(adaptationGIMMEK30,GIMMEK30Abilities,GIMMEK30Engagements,GIMMEK30PrefProfDiff,GIMMEK30ExecTime, False, 7, 9)


f = open("demofile3.txt", "w")
f.write("Woops! I have deleted the content!")
f.close()

timesteps=[i for i in range(numIterationsPerRun)]

# -------------------------------------------------------
plt.plot(timesteps, GIMME10Abilities, label=r'$GIMME 10 Samples (avg. it. exec. time = '+str(GIMME10ExecTime)+')$')
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME 100 Samples (avg. it. exec. time = '+str(GIMMEExecTime)+')$')
plt.plot(timesteps, GIMME1000Abilities, label=r'$GIMME 1000 Samples (avg. it. exec. time = '+str(GIMME1000ExecTime)+')$')
plt.plot(timesteps, GIMME2000Abilities, label=r'$GIMME 2000 Samples (avg. it. exec. time = '+str(GIMME2000ExecTime)+')$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.legend(loc='best')
plt.show()

# -------------------------------------------------------
plt.plot(timesteps, GIMMEK1Abilities, label=r'$GIMME k = 1$')
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME k = 5$')
plt.plot(timesteps, GIMMEK24Abilities, label=r'$GIMME k = 24$')
plt.plot(timesteps, GIMMEK30Abilities, label=r'$GIMME k = 30$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomAbilities, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalAbilities, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, array(optimalAbilities) - array(GIMMEAbilities), label=r'$GIMME\ strategy$')
plt.plot(timesteps, array(optimalAbilities) - array(randomAbilities), label=r'$Random\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Distance from Optimal avg Ability Increase")

plt.legend(loc='best')
plt.show()



# -------------------------------------------------------
plt.plot(timesteps, GIMMEEngagements, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomEngagements, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalEngagements, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Engagement Increase")

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, GIMMEPrefProfDiff, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomPrefProfDiff, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalPrefProfDiff, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("avg Preference Differences")

plt.legend(loc='best')
plt.show()

