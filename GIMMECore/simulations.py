import numpy
import random
import json
import copy

import time

import matplotlib.pyplot as plt
import math

import datetime
import os

from GIMMECore import *
from ModelMocks import *

import numpy

import random
random.seed(time.perf_counter())

numRuns = 100
maxNumTrainingIterations = 50
numRealIterations = 0
numTrainingCyclesPerRun = 0

playerWindow = 30

numPlayers = 23
# numPlayers -= 1 #because indeces start at 0


players = [None for x in range(numPlayers)]
tasks = [None for x in range(20)]


startTime = str(datetime.datetime.now())
newpath = "./simulationResults/" + startTime
if not os.path.exists(newpath):
    os.makedirs(newpath)
    os.makedirs(newpath+"/charts/")

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
	
	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		players[int(playerId)] = PlayerModelMock(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality)	

	def resetPlayer(self, playerId):
		players[int(playerId)].currState.reset()
		players[int(playerId)].pastModelIncreasesGrid.reset()
		# print(json.dumps(players[int(playerId)], default=lambda o: o.__dict__, sort_keys=True))

	def savePlayerState(self, playerId, increases, newState):
		players[int(playerId)].currState = newState
		players[int(playerId)].pastModelIncreasesGrid.pushToGrid(increases)

	def setBaseLearningRate(self, playerId, blr):
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
	
	increases = PlayerState()
	increases.profile = currState.profile
	increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	playerBridge.savePlayerState(playerId, increases, newState)		
	return increases

def calcReaction(state, playerBridge, playerId, interactionsProfile, currIteration):
	personality = playerBridge.getPlayerPersonality(playerId)

	# if(playerId==0):
	# 	print(json.dumps(personality, default=lambda o: o.__dict__, sort_keys=True))

	# engagement varies from 0 to 1
	state.characteristics.engagement = 0.2* (state.characteristics.engagement) + 0.8* (4.0 - personality.sqrDistanceBetween(interactionsProfile))/4.0

	abilityIncreaseSim = (playerBridge.getBaseLearningRate(x) * state.characteristics.engagement) #between 0 and 1
	state.characteristics.ability = state.characteristics.ability + abilityIncreaseSim
	
	return state


# create players, tasks and adaptation
playerBridge = CustomPlayerModelBridge()
for x in range(numPlayers):
	playerBridge.registerNewPlayer(int(x), "name", PlayerState(), PlayerStateGrid(10, 3), PlayerCharacteristics(), InteractionsProfile())
	# playerBridge.registerNewPlayer(int(x), "name", PlayerState(), PlayerStateGrid(1, playerWindow), PlayerCharacteristics(), InteractionsProfile())

# print(json.dumps(players, default=lambda o: o.__dict__, sort_keys=True))
taskBridge = CustomTaskModelBridge()
for x in range(20):
	taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), 0.5, 0.5)


adaptationGIMME = Adaptation()
adaptationGIMMEOld = Adaptation()

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
	playerBridge.setPlayerPersonality(x, InteractionsProfile(K_i=numpy.random.uniform(0, 1), K_cp=numpy.random.uniform(0, 1), K_mh=numpy.random.uniform(0, 1), K_pa=numpy.random.uniform(0, 1)))
	# playerBridge.setBaseLearningRate(x, numpy.random.normal(0.5, 0.16))
	playerBridge.setBaseLearningRate(x, numpy.clip(numpy.random.normal(0.5, 0.3),0.1,0.9))
	# print(numpy.clip(numpy.random.normal(0.5, 0.5),0.1,0.9))


# input("Press Enter to continue...")


# ------------------------------------------------------------------------------------------------------------------------------------------
preferredNumberOfPlayersPerGroup = 4

adaptationRandom.init(playerBridge, taskBridge, configsGenAlg = RandomConfigsGen(), name="", preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)

simOptimalFitness = SimulationsOptimalFitness(calcReaction, PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates
adaptationOptimal.init(playerBridge, taskBridge, configsGenAlg = OptimalPracticalConfigsGen(), fitAlg = simOptimalFitness, name="", numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
# adaptationOptimal.init(KNNRegression(5), EvolutionaryConfigsGen(), simOptimalFitness, playerBridge, taskBridge, name="", numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)

adaptationGIMME.init(playerBridge, taskBridge, regAlg = KNNRegression(5), configsGenAlg = GIMMEConfigsGen(), fitAlg = WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), name="", numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)

# ------------------------------------------------------------------------------------------------------------------------------------------

GIMMEAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
GIMMEEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
GIMMEPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
GIMMEGroupSizeFreqs = [0 for i in range(preferredNumberOfPlayersPerGroup)]
GIMMEConfigsSizeFreqs = [0 for i in range(numPlayers)]

randomAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
randomEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
randomPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]


optimalAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
optimalEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]
optimalPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations + 1)]


GIMMEExecTime = 0.0

randomExecTime = 0.0
optimalExecTime = 0.0

def executionPhase(maxNumIterations, startingI, currRun, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms):
	# for i in range(numIterationsPerRun):
	i = startingI
	lastCurrAbilityArray = []
	while(i < maxNumIterations + startingI):
		if algType == "optimal":
			simOptimalFitness.updateCurrIteration(i)

		t0 = time.perf_counter()

		print("step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun)+" of "+str(numRuns)+") of algorithm ("+str(algorithmNum)+" of "+str(numAlgorithms)+")						", end="\r")
		iteration = adaptation.iterate()

		t1 = time.perf_counter() - t0
		avgItExecTime += (t1 - t0)/(numRuns) # CPU seconds elapsed (floating point)

		currAbility = 0
		currEngagement = 0

		for x in range(numPlayers):
			increases = simulateReaction(i, playerBridge, x)
			abilityArray[i] += increases.characteristics.ability
			engagementArray[i] += increases.characteristics.engagement
			profDiffArray[i] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x))
	
		i+=1



def executeSimulations(adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms):

	totalNumIterations = (maxNumTrainingIterations + numRealIterations)
	for r in range(numRuns):
		for x in range(numPlayers):
			playerBridge.resetPlayer(x)
			
			currPersonality = InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
			playerBridge.setPlayerPersonality(x, currPersonality)
			# playerBridge.setPlayerPersonality(x, initialPersonalities[r][x])

		# algorithm training simulation 
		executionPhase(maxNumTrainingIterations, 1, r, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms)

		for x in range(numPlayers):
			currPersonality = InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
			playerBridge.setPlayerPersonality(x, currPersonality)
			# playerBridge.setPlayerPersonality(x, modifiedPersonalities[r][x])

		# algorithm applied to real scenario simulation 
		executionPhase(numRealIterations, maxNumTrainingIterations+1, r, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms)

	avgItExecTime /= totalNumIterations
	for x in range(totalNumIterations+1):
		abilityArray[x] /= (numPlayers * numRuns)
		engagementArray[x] /= (numPlayers * numRuns)
		profDiffArray[x] /= (numPlayers * numRuns)
	
	groupSizeFreqs = adaptation.configsGenAlg.groupSizeFreqs
	configSizeFreqs = adaptation.configsGenAlg.configSizeFreqs
	if canExport == True:
		f = open(newpath+"/"+algorithmFilename+".txt", "w")
		f.write("abilities: "+json.dumps(abilityArray))
		f.write("\nengagements: "+json.dumps(engagementArray))
		f.write("\nprofDiffArray: "+json.dumps(profDiffArray))
		f.close()

# executeSimulations(adaptationGIMME, GIMMEAbilities, GIMMEEngagements, GIMMEPrefProfDiff, GIMMEGroupSizeFreqs, GIMMEConfigsSizeFreqs, GIMMEExecTime, "GIMME", "adaptationGIMME", True,  2, 9)

executeSimulations(adaptationOptimal, optimalAbilities, optimalEngagements, optimalPrefProfDiff, [], [], optimalExecTime, "optimal", "adaptationOptimal", True, 9, 9)
# executeSimulations(adaptationRandom, randomAbilities, randomEngagements, randomPrefProfDiff, [], [], randomExecTime, "random", "adaptationRandom", True,  8, 9)

# quit()

timesteps=[i for i in range(maxNumTrainingIterations + numRealIterations + 1)]
# # -------------------------------------------------------
# plt.plot(timesteps, GIMME10Abilities, label=r'$GIMME 10 Samples (avg. it. exec. time = '+str(GIMME10ExecTime)+')$')
# plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME 100 Samples (avg. it. exec. time = '+str(GIMMEExecTime)+')$')
# plt.plot(timesteps, GIMME1000Abilities, label=r'$GIMME 1000 Samples (avg. it. exec. time = '+str(GIMME1000ExecTime)+')$')
# plt.plot(timesteps, GIMME2000Abilities, label=r'$GIMME 2000 Samples (avg. it. exec. time = '+str(GIMME2000ExecTime)+')$')

# plt.xlabel("Iteration")
# plt.ylabel("avg Ability Increase")

# plt.savefig(newpath+'/charts/simulationsResultsNSamplesComparison.png')

# plt.legend(loc='best')
# plt.show()

# # -------------------------------------------------------
# plt.plot(timesteps, GIMMEK1Abilities, label=r'$GIMME k = 1$')
# plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME k = 5$')
# plt.plot(timesteps, GIMMEK24Abilities, label=r'$GIMME k = 24$')
# plt.plot(timesteps, GIMMEK30Abilities, label=r'$GIMME k = 30$')

# plt.xlabel("Iteration")
# plt.ylabel("avg Ability Increase")

# plt.savefig(newpath+'/charts/simulationsResultsNSamplesAndNNsComparison.png')

# plt.legend(loc='best')
# plt.show()


# -------------------------------------------------------
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomAbilities, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalAbilities, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.savefig(newpath+'/charts/simulationsResultsAbility_old.png')

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, numpy.array(optimalAbilities) - numpy.array(GIMMEAbilities), label=r'$GIMME\ strategy$')
plt.plot(timesteps, numpy.array(optimalAbilities) - numpy.array(randomAbilities), label=r'$Random\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Distance from Optimal avg Ability Increase")

plt.savefig(newpath+'/charts/simulationsResultsAbility.png')

plt.legend(loc='best')
plt.show()



# -------------------------------------------------------
plt.plot(timesteps, GIMMEEngagements, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomEngagements, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalEngagements, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Engagement Increase")

plt.savefig(newpath+'/charts/simulationsResultsEngagement.png')

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, GIMMEPrefProfDiff, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomPrefProfDiff, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalPrefProfDiff, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("avg Preference Differences")

plt.savefig(newpath+'/charts/simulationsResultsProfileDist.png')

plt.legend(loc='best')
plt.show()

