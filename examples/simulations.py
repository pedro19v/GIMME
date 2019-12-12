import random
import json
import copy
import time
import matplotlib.pyplot as plt
import math
import os
import sys
import datetime

import matplotlib.pyplot as plt
from numpy import array
import matplotlib.collections as collections

from GIMMECore import *
from ModelMocks import *

plt.style.use('tableau-colorblind10')
random.seed(time.perf_counter())

numRuns = 300
maxNumTrainingIterations = 40
numRealIterations = 15

playerWindow = 30
numPlayers = 23

startTime = str(datetime.datetime.now())
newpath = "./simulationResults/" + startTime +" numRuns:" + str(numRuns) + ",maxNumTrainingIterations: " + str(maxNumTrainingIterations) + ", numRealIterations: " + str(numRealIterations)
if not os.path.exists(newpath):
    os.makedirs(newpath)
    os.makedirs(newpath+"/charts/")


def simulateReaction(playerBridge, currIteration, playerId):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(playerBridge, currState, playerId, currState.profile, currIteration)

	increases = PlayerState()
	increases.profile = currState.profile
	increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	playerBridge.savePlayerState(playerId, increases, newState)	
	return increases

def calcReaction(playerBridge, state, playerId, interactionsProfile, currIteration):
	personality = playerBridge.getPlayerPersonality(playerId)
	newState = PlayerState(characteristics = PlayerCharacteristics(ability=state.characteristics.ability, engagement=state.characteristics.engagement), profile=state.profile)
	newState.characteristics.engagement = 0.05* (newState.characteristics.engagement) + 0.95* (2.0 - personality.distanceBetween(interactionsProfile))/2.0  #between 0 and 1
	abilityIncreaseSim = (newState.characteristics.engagement**playerBridge.getBaseLearningRate(playerId))
	newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
	return newState

def executionPhase(playerBridge, maxNumIterations, startingI, currRun, adaptation, \
	abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, \
	canExport, algorithmNum, numAlgorithms):
	i = startingI
	while(i < maxNumIterations + startingI):
		if adaptation.name == "optimal":
			accurateConfigsAlg.updateCurrIteration(i)
		
		t0 = time.perf_counter()

		print("step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun)+" of "+str(numRuns)+") of algorithm ("+str(algorithmNum)+" of "+str(numAlgorithms)+")						", end="\r")
		adaptation.iterate()

		t1 = time.perf_counter() - t0
		avgItExecTime += (t1 - t0)/(numRuns) # CPU seconds elapsed (floating point)

		currAbility = 0
		currEngagement = 0

		for x in range(numPlayers):
			increases = simulateReaction(playerBridge, i, x)
			abilityMatrix[i][currRun] += increases.characteristics.ability / numPlayers
			engagementMatrix[i][currRun] += increases.characteristics.engagement / numPlayers
			profDiffMatrix[i][currRun] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / numPlayers
		i+=1



def executeSimulations(playerBridge, taskBridge, adaptation, \
	abilityMean, abilitySTDev, engagementMean, engagementSTDev, profDiffMean, profDiffSTDev, avgItExecTime,\
	canExport, algorithmNum, numAlgorithms):

	abilityMatrix = [[0 for i in range(numRuns)] for y in range(maxNumTrainingIterations + numRealIterations)]
	engagementMatrix = [[0 for i in range(numRuns)] for y in range(maxNumTrainingIterations + numRealIterations)]
	profDiffMatrix = [[0 for i in range(numRuns)] for y in range(maxNumTrainingIterations + numRealIterations)]

	adaptationName = adaptation.getName()

	# create players and tasks
	for x in range(numPlayers):
		if adaptationName == "GIMMEGrid":
			playerBridge.registerNewPlayer(int(x), "name", PlayerState(time.time()), PlayerStateGrid(numCells = 16, maxProfilesPerCell = 2), PlayerCharacteristics(), InteractionsProfile())
		else:
			playerBridge.registerNewPlayer(int(x), "name", PlayerState(time.time()), PlayerStateGrid(numCells = 1, maxProfilesPerCell = playerWindow), PlayerCharacteristics(), InteractionsProfile())
	for x in range(20):
		taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), datetime.timedelta(minutes=1), 0.5, 0.5)


	totalNumIterations = (maxNumTrainingIterations + numRealIterations)
	for r in range(numRuns):
		# init players
		for x in range(numPlayers):
			adaptation.configsGenAlg.reset()
			playerBridge.resetPlayer(x)
			playerBridge.setPlayerPersonality(x, InteractionsProfile(K_i=random.uniform(0.0, 1.0), K_cp=random.uniform(0.0, 1.0), K_mh=random.uniform(0.0, 1.0), K_ea=random.uniform(0.0, 1.0)))
			playerBridge.setBaseLearningRate(x, random.gauss(0.5, 0.16))

		executionPhase(playerBridge, maxNumTrainingIterations, 0, r, adaptation, abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, canExport, algorithmNum, numAlgorithms)
		
		# players change preferences
		for x in range(numPlayers):
			playerBridge.setPlayerPersonality(x, InteractionsProfile(K_i=random.uniform(0.0, 1.0), K_cp=random.uniform(0.0, 1.0), K_mh=random.uniform(0.0, 1.0), K_ea=random.uniform(0.0, 1.0)))

		executionPhase(playerBridge, numRealIterations, maxNumTrainingIterations, r, adaptation, abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, canExport, algorithmNum, numAlgorithms)

	# finish to calculate means and std devs for charts
	avgItExecTime /= totalNumIterations
	for i in range(totalNumIterations):
		for r in range(numRuns):
			abilityMean[i] += abilityMatrix[i][r]
			engagementMean[i] += engagementMatrix[i][r]
			profDiffMean[i] += profDiffMatrix[i][r]

			abilitySTDev[i] += abilityMatrix[i][r]**2
			engagementSTDev[i] += engagementMatrix[i][r]**2
			profDiffSTDev[i] += profDiffMatrix[i][r]**2
		
		abilityMean[i] /= numRuns
		engagementMean[i] /= numRuns
		profDiffMean[i] /= numRuns

		abilitySTDev[i] /= numRuns
		engagementSTDev[i] /= numRuns
		profDiffSTDev[i] /= numRuns

		abilitySTDev[i] = math.sqrt((abilitySTDev[i] - abilityMean[i]**2) * (numRuns/(numRuns - 1)))
		engagementSTDev[i] = math.sqrt((engagementSTDev[i] - engagementMean[i]**2) * (numRuns/(numRuns - 1)))
		profDiffSTDev[i] = math.sqrt((profDiffSTDev[i] - profDiffMean[i]**2) * (numRuns/(numRuns - 1)))
	
	groupSizeFreqs = adaptation.configsGenAlg.groupSizeFreqs
	configSizeFreqs = adaptation.configsGenAlg.configSizeFreqs

	if canExport == True:
		f = open(newpath+"/"+adaptationName+".txt", "w")
		f.write(adaptationName+"AbilityMeans = "+json.dumps(abilityMean)+"\n")
		f.write(adaptationName+"AbilitySTDev = "+json.dumps(abilitySTDev)+"\n")
		f.write(adaptationName+"EngagementMeans = "+json.dumps(engagementMean)+"\n")
		f.write(adaptationName+"EngagementSTDev = "+json.dumps(engagementSTDev)+"\n")
		f.write(adaptationName+"ProfDiffMeans = "+json.dumps(profDiffMean)+"\n")
		f.write(adaptationName+"ProfDiffSTDev = "+json.dumps(profDiffSTDev)+"\n")
		f.close()


players = [0 for x in range(numPlayers)]
playersGrid = [0 for x in range(numPlayers)]
tasks = [0 for x in range(20)]

# ----------------------- [Init Bridges] --------------------------------
playerBridgeGrid = CustomPlayerModelBridge(playersGrid)
playerBridge = CustomPlayerModelBridge(players)

taskBridge = CustomTaskModelBridge(tasks)

# ----------------------- [Init Adaptations] --------------------------------
adaptationGIMME = Adaptation()
adaptationGIMMEGrid = Adaptation()
adaptationGIMMEEv = Adaptation()


adaptationRandom = Adaptation()
adaptationOptimal = Adaptation()


# ----------------------- [Init Algorithms] --------------------------------
preferredNumberOfPlayersPerGroup = 4

simpleConfigsAlgGrid = SimpleConfigsGen(playerBridgeGrid, regAlg = KNNRegression(playerBridgeGrid, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMMEGrid.init(playerBridgeGrid, taskBridge, configsGenAlg = simpleConfigsAlgGrid, name="GIMMEGrid")

simpleConfigsAlg = SimpleConfigsGen(playerBridge, regAlg = KNNRegression(playerBridge, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg, name="GIMME")

# evConfigsAlgGrid = EvolutionaryConfigsGen(playerBridge, regAlg = KNNRegression(playerBridge, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, fitnessWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
# adaptationGIMMEEv.init(playerBridge, taskBridge, configsGenAlg = evConfigsAlgGrid, name="")

randomConfigsAlg = RandomConfigsGen(playerBridge, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationRandom.init(playerBridge, taskBridge, configsGenAlg = randomConfigsAlg, name="random")

accurateConfigsAlg = AccurateConfigsGen(playerBridge, calcReaction, numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates
adaptationOptimal.init(playerBridge, taskBridge, configsGenAlg = accurateConfigsAlg, name="optimal")


# ----------------------- [Create Arrays] --------------------------------

GIMMEAbilityMean = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEExecTime = 0.0

GIMMEGridAbilityMean = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagementMean = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridProfDiffMean = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridExecTime = 0.0

GIMMEEvAbilities = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvEngagements = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvPrefProfDiff = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvExecTime = 0.0

randomAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
randomEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomExecTime = 0.0

optimalAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
optimalEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalExecTime = 0.0


# ----------------------- [Execute Algorithms] ----------------------------
executeSimulations(playerBridge, taskBridge, adaptationRandom, randomAbilityMeans, randomAbilitySTDev, randomEngagementMeans, randomEngagementSTDev, randomProfDiffMeans, randomProfDiffSTDev, randomExecTime, True,  1, 4)
executeSimulations(playerBridge, taskBridge, adaptationGIMME, GIMMEAbilityMean, GIMMEAbilitySTDev, GIMMEEngagementMeans, GIMMEEngagementSTDev, GIMMEProfDiffMeans, GIMMEProfDiffSTDev, GIMMEExecTime, True,  2, 4)
# executeSimulations(playerBridge, taskBridge, adaptationGIMMEEv, GIMMEEvAbilities, GIMMEEvEngagements, GIMMEEvPrefProfDiff, GIMMEEvGroupSizeFreqs, GIMMEEvConfigsSizeFreqs, GIMMEExecTime, "GIMME", "adaptationGIMME", True,  3, 4)
executeSimulations(playerBridge, taskBridge, adaptationOptimal, optimalAbilityMeans, optimalAbilitySTDev, optimalEngagementMeans, optimalEngagementSTDev, optimalProfDiffMeans, optimalProfDiffSTDev, optimalExecTime, True, 3, 4)
executeSimulations(playerBridgeGrid, taskBridge, adaptationGIMMEGrid, GIMMEGridAbilityMean, GIMMEGridAbilitySTDev, GIMMEGridEngagementMean, GIMMEGridEngagementSTDev, GIMMEGridProfDiffMean, GIMMEGridProfDiffSTDev, GIMMEGridExecTime, True,  4, 4)


# ----------------------- [Generate Plots] --------------------------------
timesteps=[i for i in range(maxNumTrainingIterations + numRealIterations)]
convValue=[1.0 for i in range(maxNumTrainingIterations + numRealIterations)]
empConvValue=[optimalAbilityMeans[-1] for i in range(maxNumTrainingIterations + numRealIterations)]


plt.rcParams.update({'font.size': 22})

fig = plt.figure()
ax = fig.add_subplot(111)
c1 = collections.BrokenBarHCollection([(0,40)], (0.74,0.12), facecolor='#f7e4d4', alpha=0.5)
c2 = collections.BrokenBarHCollection([(40,15)], (0.74,0.12), facecolor='#bdedcf', alpha=0.5)
ax.add_collection(c1)
ax.add_collection(c2)

plt.errorbar(timesteps, GIMMEAbilityMean, GIMMEAbilitySTDev, marker='s', capsize=2.0, alpha=0.5, label="GIMME strategy")
plt.errorbar(timesteps, GIMMEGridAbilityMean, GIMMEGridAbilitySTDev, marker='s', capsize=2.0, alpha=0.5, label="GIMME Grid strategy")
# plt.plot(timesteps, GIMMEEvAbilities, label="GIMME Ev strategy")
plt.errorbar(timesteps, randomAbilityMeans, randomAbilitySTDev, marker='s', capsize=2.0, alpha=0.5, label="Random strategy")
plt.plot(timesteps, empConvValue, linestyle= "--", label="\"Perfect Information\" convergence value")
plt.xlabel("Iteration", fontsize=30)
plt.ylabel("avg. Ability Increase", fontsize=30)
plt.legend(loc='best', fontsize=20)

plt.savefig(newpath+'/charts/simulationsResultsAbility.png')
plt.show()


empConvValue=[optimalProfDiffMeans[-1] for i in range(maxNumTrainingIterations + numRealIterations)]

plt.errorbar(timesteps, GIMMEProfDiffMeans, GIMMEProfDiffSTDev, marker='s', capsize=2.0, alpha=0.5, label="GIMME strategy")
plt.errorbar(timesteps, GIMMEGridProfDiffMean, GIMMEGridProfDiffSTDev, marker='s', capsize=2.0, alpha=0.5, label="GIMME Grid strategy")
plt.errorbar(timesteps, randomProfDiffMeans, randomProfDiffSTDev, marker='s', capsize=2.0, alpha=0.5, label="Random strategy")
plt.plot(timesteps, empConvValue, linestyle= "--", label="\"Perfect Information\" convergence value")
plt.xlabel("Iteration", fontsize=30)
plt.ylabel("avg. Ability Increase", fontsize=30)
plt.legend(loc='best', fontsize=20)

plt.savefig(newpath+'/charts/simulationsResultsProfileDist.png')
plt.show()

