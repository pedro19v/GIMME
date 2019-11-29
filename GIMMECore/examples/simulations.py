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

from ModelMocks import *

plt.style.use('tableau-colorblind10')
random.seed(time.perf_counter())

numRuns = 3
maxNumTrainingIterations = 30
numRealIterations = 10

playerWindow = 30


startTime = str(datetime.datetime.now())
newpath = "./simulationResults/" + startTime +" numRuns:" + str(numRuns) + ",maxNumTrainingIterations: " + str(maxNumTrainingIterations) + ", numRealIterations: " + str(numRealIterations)
if not os.path.exists(newpath):
    os.makedirs(newpath)
    os.makedirs(newpath+"/charts/")


def simulateReaction(currIteration, playerBridge, playerId):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(currState, playerBridge, playerId, currState.profile, currIteration)

	increases = PlayerState()
	increases.profile = currState.profile
	increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	playerBridge.savePlayerState(playerId, increases, newState)	
	return increases

def calcReaction(state, playerBridge, playerId, interactionsProfile, currIteration):
	personality = playerBridge.getPlayerPersonality(playerId)
	newState = PlayerState(characteristics = PlayerCharacteristics(ability=state.characteristics.ability, engagement=state.characteristics.engagement), profile=state.profile)
	newState.characteristics.engagement = 0.05* (newState.characteristics.engagement) + 0.95* (2.0 - personality.distanceBetween(interactionsProfile))/2.0  #between 0 and 1
	abilityIncreaseSim = (newState.characteristics.engagement**playerBridge.getBaseLearningRate(playerId))
	newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
	return newState

def executionPhase(maxNumIterations, startingI, currRun, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms):
	i = startingI
	lastCurrAbilityArray = []
	while(i < maxNumIterations + startingI):
		if algType == "optimal":
			simOptimalConfigsAlg.updateCurrIteration(i)
		
		t0 = time.perf_counter()

		print("step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun)+" of "+str(numRuns)+") of algorithm ("+str(algorithmNum)+" of "+str(numAlgorithms)+")						", end="\r")
		adaptation.iterate()

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
	# create players and tasks
	playerBridge = adaptation.playerModelBridge
	for x in range(numPlayers):
		playerBridge.registerNewPlayer(int(x), "name", PlayerState(time.time()), PlayerStateGrid(1, playerWindow), PlayerCharacteristics(), InteractionsProfile())
		playerBridgeGrid.registerNewPlayer(int(x), "name", PlayerState(time.time()), PlayerStateGrid(2, 16), PlayerCharacteristics(), InteractionsProfile())

	# print(json.dumps(players, default=lambda o: o.__dict__, sort_keys=True))
	taskBridge = adaptation.taskModelBridge
	for x in range(20):
		taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), 0.5, 0.5)


	totalNumIterations = (maxNumTrainingIterations + numRealIterations)
	for r in range(numRuns):
		# init players
		for x in range(numPlayers):
			adaptation.configsGenAlg.reset()
			playerBridge.resetPlayer(x)
			playerBridge.setPlayerPersonality(x, InteractionsProfile(K_i=random.uniform(0.0, 1.0), K_cp=random.uniform(0.0, 1.0), K_mh=random.uniform(0.0, 1.0), K_pa=random.uniform(0.0, 1.0)))
			playerBridge.setBaseLearningRate(x, random.gauss(0.5, 0.16))
			# playerBridge.setBaseLearningRate(x, random.uniform(0.0, 1.0))

		executionPhase(maxNumTrainingIterations, 0, r, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms)

		# players change preferences
		for x in range(numPlayers):
			currPersonality = InteractionsProfile(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
			playerBridge.setPlayerPersonality(x, currPersonality)

		executionPhase(numRealIterations, maxNumTrainingIterations, r, adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms)

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



playerBridge = CustomPlayerModelBridge()
taskBridge = CustomTaskModelBridge()
playerBridgeGrid = CustomPlayerModelBridgeGrid()

adaptationGIMME = Adaptation()
adaptationGIMMEGrid = Adaptation()
adaptationGIMMEEv = Adaptation()


adaptationRandom = Adaptation()
adaptationOptimal = Adaptation()


# ----------------------- [Init Algorithms] --------------------------------
preferredNumberOfPlayersPerGroup = 4

adaptationGIMME.init(playerBridge, taskBridge, regAlg = KNNRegression(3), configsGenAlg = GIMMEConfigsGen(), fitAlg = WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), name="", numberOfConfigChoices=50, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationGIMMEGrid.init(playerBridgeGrid, taskBridge, regAlg = KNNRegression(3), configsGenAlg = GIMMEConfigsGen(), fitAlg = WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), name="", numberOfConfigChoices=50, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
# adaptationGIMMEEv.init(playerBridge, taskBridge, regAlg = KNNRegression(3), configsGenAlg = EvolutionaryConfigsGen(numMutations=100,probOfMutation=0.2), fitAlg = WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), name="", numberOfConfigChoices=10, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)

adaptationRandom.init(playerBridge, taskBridge, configsGenAlg = RandomConfigsGen(), name="", preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)

simOptimalConfigsAlg = OptimalPracticalConfigsGen(calcReaction) #needed for currIteration updates
adaptationOptimal.init(playerBridge, taskBridge, configsGenAlg = simOptimalConfigsAlg, fitAlg = WeightedFitness(PlayerCharacteristics(ability=1.0, engagement=0.0)), name="", numberOfConfigChoices=50, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)


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
# executeSimulations(adaptationGIMMEEv, GIMMEEvAbilities, GIMMEEvEngagements, GIMMEEvPrefProfDiff, GIMMEEvGroupSizeFreqs, GIMMEEvConfigsSizeFreqs, GIMMEExecTime, "GIMME", "adaptationGIMME", True,  2, 9)
executeSimulations(adaptationRandom, randomAbilities, randomEngagements, randomPrefProfDiff, [], [], randomExecTime, "random", "adaptationRandom", True,  8, 9)
# executeSimulations(adaptationOptimal, optimalAbilities, optimalEngagements, optimalPrefProfDiff, [], [], optimalExecTime, "optimal", "adaptationOptimal", True, 9, 9)
executeSimulations(adaptationGIMME, GIMMEAbilities, GIMMEEngagements, GIMMEPrefProfDiff, GIMMEGroupSizeFreqs, GIMMEConfigsSizeFreqs, GIMMEExecTime, "GIMME", "adaptationGIMME", True,  2, 9)
executeSimulations(adaptationGIMMEGrid, GIMMEGridAbilities, GIMMEGridEngagements, GIMMEGridPrefProfDiff, GIMMEGridGroupSizeFreqs, GIMMEGridConfigsSizeFreqs, GIMMEGridExecTime, "GIMME", "adaptationGIMME", True,  2, 9)

# ----------------------- [Generate Plots] --------------------------------
timesteps=[i for i in range(maxNumTrainingIterations + numRealIterations)]
convValue=[1.0 for i in range(maxNumTrainingIterations + numRealIterations)]

plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME\ strategy$')
plt.plot(timesteps, GIMMEGridAbilities, label=r'$GIMME\ Grid\ strategy$')
# plt.plot(timesteps, GIMMEEvAbilities, label=r'$GIMME\ Ev\ strategy$')
plt.plot(timesteps, randomAbilities, label=r'$Random\ strategy$')
plt.plot(timesteps, convValue, linestyle= "--", label=r'$Expected convergence value$')
# plt.plot(timesteps, optimalAbilities, label=r'$Optimal\ strategy$')
plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")
plt.legend(loc='best')

plt.savefig(newpath+'/charts/simulationsResultsAbility.png')
plt.show()


# -------------------------------------------------------
convValue=[0.0 for i in range(maxNumTrainingIterations + numRealIterations)]

plt.plot(timesteps, GIMMEPrefProfDiff, label=r'$GIMME\ strategy$')
plt.plot(timesteps, GIMMEGridProfDiff, label=r'$GIMME\ Grid\ strategy$')
# plt.plot(timesteps, GIMMEEvPrefProfDiff, label=r'$GIMME\ Ev\ strategy$')
plt.plot(timesteps, randomPrefProfDiff, label=r'$Random\ strategy$')
# plt.plot(timesteps, optimalPrefProfDiff, label=r'$Optimal\ strategy$')
plt.plot(timesteps, convValue, linestyle= "--", label=r'$Expected convergence value$')

plt.xlabel("Iteration")
plt.ylabel("avg Preference Differences")
plt.legend(loc='best')

plt.savefig(newpath+'/charts/simulationsResultsProfileDist.png')
plt.show()

