import random
import json
import copy
import time
import matplotlib.pyplot as plt
import math
import os
import sys
import datetime
sys.path.append(os.path.join(sys.path[0],'..'))
from ModelMocks import *

plt.style.use('tableau-colorblind10')
random.seed(time.perf_counter())

numRuns = 1
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

def executionPhase(playerBridge, maxNumIterations, startingI, currRun, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms):
	i = startingI
	lastCurrAbilityArray = []
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
			abilityArray[i] += increases.characteristics.ability
			engagementArray[i] += increases.characteristics.engagement
			profDiffArray[i] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x))
		i+=1



def executeSimulations(playerBridge, taskBridge, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms):

	# create players and tasks
	for x in range(numPlayers):
		if algType == "GIMMEGrid":
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

		executionPhase(playerBridge, maxNumTrainingIterations, 0, r, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms)
		
		# players change preferences
		for x in range(numPlayers):
			playerBridge.setPlayerPersonality(x, InteractionsProfile(K_i=random.uniform(0.0, 1.0), K_cp=random.uniform(0.0, 1.0), K_mh=random.uniform(0.0, 1.0), K_ea=random.uniform(0.0, 1.0)))

		executionPhase(playerBridge, numRealIterations, maxNumTrainingIterations, r, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms)

	avgItExecTime /= totalNumIterations
	for x in range(totalNumIterations):
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
adaptationGIMMEGrid.init(playerBridgeGrid, taskBridge, configsGenAlg = simpleConfigsAlgGrid, name="")

simpleConfigsAlg = SimpleConfigsGen(playerBridge, regAlg = KNNRegression(playerBridge, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg, name="")

evConfigsAlgGrid = EvolutionaryConfigsGen(playerBridge, regAlg = KNNRegression(playerBridge, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, fitnessWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMMEEv.init(playerBridge, taskBridge, configsGenAlg = evConfigsAlgGrid, name="")


randomConfigsAlg = RandomConfigsGen(playerBridge, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationRandom.init(playerBridge, taskBridge, configsGenAlg = randomConfigsAlg, name="")

accurateConfigsAlg = AccurateConfigsGen(playerBridge, calcReaction, numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates
adaptationOptimal.init(playerBridge, taskBridge, configsGenAlg = accurateConfigsAlg, name="")


# ----------------------- [Create Arrays] --------------------------------
GIMMEAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGroupSizeFreqs = [0 for i in range(preferredNumberOfPlayersPerGroup)]
GIMMEConfigsSizeFreqs = [0 for i in range(numPlayers)]
GIMMEExecTime = 0.0

GIMMEGridAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridGroupSizeFreqs = [0 for i in range(preferredNumberOfPlayersPerGroup)]
GIMMEGridConfigsSizeFreqs = [0 for i in range(numPlayers)]
GIMMEGridExecTime = 0.0

GIMMEEvAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEvGroupSizeFreqs = [0 for i in range(preferredNumberOfPlayersPerGroup)]
GIMMEEvConfigsSizeFreqs = [0 for i in range(numPlayers)]
GIMMEEvExecTime = 0.0

randomAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
randomEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
randomPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
randomExecTime = 0.0

optimalAbilities = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
optimalEngagements = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
optimalPrefProfDiff = [0 for i in range(maxNumTrainingIterations + numRealIterations)]
optimalExecTime = 0.0


# ----------------------- [Execute Algorithms] ----------------------------
executeSimulations(playerBridge, taskBridge, adaptationRandom, randomAbilities, randomEngagements, randomPrefProfDiff, [], [], randomExecTime, "random", "Random", True,  1, 4)
executeSimulations(playerBridge, taskBridge, adaptationGIMME, GIMMEAbilities, GIMMEEngagements, GIMMEPrefProfDiff, GIMMEGroupSizeFreqs, GIMMEConfigsSizeFreqs, GIMMEExecTime, "GIMME", "GIMME", True,  2, 4)
# executeSimulations(playerBridge, taskBridge, adaptationGIMMEEv, GIMMEEvAbilities, GIMMEEvEngagements, GIMMEEvPrefProfDiff, GIMMEEvGroupSizeFreqs, GIMMEEvConfigsSizeFreqs, GIMMEExecTime, "GIMME", "adaptationGIMME", True,  3, 4)
executeSimulations(playerBridge, taskBridge, adaptationOptimal, optimalAbilities, optimalEngagements, optimalPrefProfDiff, [], [], optimalExecTime, "optimal", "adaptationOptimal", True, 9, 9)
executeSimulations(playerBridgeGrid, taskBridge, adaptationGIMMEGrid, GIMMEGridAbilities, GIMMEGridEngagements, GIMMEGridPrefProfDiff, GIMMEGridGroupSizeFreqs, GIMMEGridConfigsSizeFreqs, GIMMEGridExecTime, "GIMMEGrid", "GIMMEGrid", True,  4, 4)


# ----------------------- [Generate Plots] --------------------------------
timesteps=[i for i in range(maxNumTrainingIterations + numRealIterations)]
convValue=[1.0 for i in range(maxNumTrainingIterations + numRealIterations)]
empConvValue=[optimalAbilities[-1] for i in range(maxNumTrainingIterations + numRealIterations)]

plt.plot(timesteps, GIMMEAbilities, label="GIMME strategy")
plt.plot(timesteps, GIMMEGridAbilities, label="GIMME Grid strategy")
# plt.plot(timesteps, GIMMEEvAbilities, label="GIMME Ev strategy")
plt.plot(timesteps, randomAbilities, label="Random strategy")
# plt.plot(timesteps, convValue, linestyle= "--", label=r'$Expected convergence value$')
plt.plot(timesteps, empConvValue, linestyle= "--", label="\"Perfect Information\" convergence value")
plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")
plt.legend(loc='best')

plt.savefig(newpath+'/charts/simulationsResultsAbility.png')
plt.show()


empConvValue=[optimalPrefProfDiff[-1] for i in range(maxNumTrainingIterations + numRealIterations)]
plt.plot(timesteps, GIMMEPrefProfDiff, label="GIMME strategy")
plt.plot(timesteps, GIMMEGridPrefProfDiff, label="GIMME Grid strategy")
# plt.plot(timesteps, GIMMEEvPrefProfDiff, label="GIMME Ev strategy")
plt.plot(timesteps, randomPrefProfDiff, label="Random strategy")
plt.plot(timesteps, optimalPrefProfDiff, label=r'$Optimal\ strategy$')
plt.plot(timesteps, empConvValue, linestyle= "--", label="\"Perfect Information\" convergence value")

plt.xlabel("Iteration")
plt.ylabel("avg Preference Differences")
plt.legend(loc='best')

plt.savefig(newpath+'/charts/simulationsResultsProfileDist.png')
plt.show()

