import numpy
import random
import json
import copy

import time

import matplotlib.pyplot as plt
import math


from GIMMECore import *
from ModelMocks import *


t0 = time.clock()


numRuns = 1
numIterationsPerRun = 30
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

	def resetPlayerPastModelIncreases(self, playerId):
		players[int(playerId)].pastModelIncreasesGrid.reset()

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

	def resetPlayer(self, playerId):
		return 0


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
	inherentPreference = playerBridge.getInherentPreference(playerId)
	state.characteristics.engagement = 0.5* (state.characteristics.engagement) + 0.5* (1.0 - inherentPreference.distanceBetween(interactionsProfile))

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
adaptationRandom = Adaptation()
adaptationOptimal = Adaptation()



# init players
for x in range(numPlayers):
	playerBridge.saveInherentPreference(x, InteractionsProfile(K_i=numpy.random.uniform(0, 1), K_cp=numpy.random.uniform(0, 1), K_mh=numpy.random.uniform(0, 1), K_pa=numpy.random.uniform(0, 1)))
	playerBridge.saveBaseLearningRate(x, numpy.random.uniform(0.2, 0.6))
	playerBridge.initIterationReactions(x, [0]*numIterationsPerRun)

	for p in range(playerWindow):
		playerBridge.saveIterationReaction(x, p, numpy.random.normal(playerBridge.getBaseLearningRate(x), 0.05))



simOptimalFitness = SimulationsOptimalFitness(calcReaction, PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates

adaptationGIMME.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationRandom.init(KNNRegression(5), RandomConfigsGen(), RandomFitness(), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)
adaptationOptimal.init(KNNRegression(5), RandomConfigsGen(), simOptimalFitness, playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)


GIMMEAbilities = [0 for i in range(numIterationsPerRun)]
GIMMEEngagements = [0 for i in range(numIterationsPerRun)]
GIMMEPrefProfDiff = [0 for i in range(numIterationsPerRun)]


randomAbilities = [0 for i in range(numIterationsPerRun)]
randomEngagements = [0 for i in range(numIterationsPerRun)]
randomPrefProfDiff = [0 for i in range(numIterationsPerRun)]


optimalAbilities = [0 for i in range(numIterationsPerRun)]
optimalEngagements = [0 for i in range(numIterationsPerRun)]
optimalPrefProfDiff = [0 for i in range(numIterationsPerRun)]

def executeSimulations(adaptation,abilityArray,engagementArray,profDiffArray, isOptimalRun):
	for r in range(numRuns):
		for x in range(numPlayers):
			playerBridge.resetPlayerPastModelIncreases(x)

		for i in range(numTrainingCyclesPerRun):
			for x in range(numPlayers):
				simulateReaction(i, playerBridge, x) 

		for i in range(numIterationsPerRun):
			if isOptimalRun == True:
				simOptimalFitness.updateCurrIteration(i)


			print("step " +str(i)+ " of "+str(numIterationsPerRun)+" of run "+str(r)+"						", end="\r")
			iteration = adaptation.iterate()

			for x in range(numPlayers):
				abilityArray[i] += playerBridge.getPlayerCurrCharacteristics(x).ability / (numIterationsPerRun*numRuns)
				engagementArray[i] += playerBridge.getPlayerCurrCharacteristics(x).engagement / (numIterationsPerRun*numRuns)
				profDiffArray[i] += playerBridge.getInherentPreference(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / (numIterationsPerRun*numRuns)
				simulateReaction(i, playerBridge, x)

executeSimulations(adaptationGIMME,GIMMEAbilities,GIMMEEngagements,GIMMEPrefProfDiff, False)
executeSimulations(adaptationRandom,randomAbilities,randomEngagements,randomPrefProfDiff, False)
executeSimulations(adaptationOptimal,optimalAbilities,optimalEngagements,optimalPrefProfDiff,True)


# GIMMEAbilities = [0] + GIMMEAbilities
# GIMMEEngagements = [0] + GIMMEEngagements
# GIMMEPrefProfDiff = [0] + GIMMEPrefProfDiff


t1 = time.clock() - t0
print("Time elapsed: ", t1 - t0) # CPU seconds elapsed (floating point)


timesteps=[i for i in range(numIterationsPerRun)]

plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME\ group\ formation\ strategy$')
plt.plot(timesteps, randomAbilities, label=r'$Random\ group\ formation\ strategy$')
plt.plot(timesteps, optimalAbilities, label=r'$Optimal\ group\ formation\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Ability Increase")

plt.legend(loc='best')
plt.show()



plt.plot(timesteps, GIMMEEngagements, label=r'$GIMME\ group\ formation\ strategy$')
plt.plot(timesteps, randomEngagements, label=r'$Random\ group\ formation\ strategy$')
plt.plot(timesteps, optimalEngagements, label=r'$Optimal\ group\ formation\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Engagement Increase")

plt.legend(loc='best')
plt.show()


plt.plot(timesteps, GIMMEPrefProfDiff, label=r'$GIMME\ group\ formation\ strategy$')
plt.plot(timesteps, randomPrefProfDiff, label=r'$Random\ group\ formation\ strategy$')
plt.plot(timesteps, optimalPrefProfDiff, label=r'$Optimal\ group\ formation\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("prof diff Increase")

plt.legend(loc='best')
plt.show()

