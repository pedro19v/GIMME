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
from LogManager import *

random.seed(time.perf_counter())
simsID = seed = random.randrange(sys.maxsize)

numRuns = 25
maxNumTrainingIterations = 20
numRealIterations = 20

preferredNumberOfPlayersPerGroup = 4
numberOfConfigChoices = 100

numTestedPlayerProfilesInEst = 500

playerWindow = 10
numPlayers = 23

numTasks = 20

startTime = str(datetime.datetime.now())
newpath = "./simulationResults/latestResults/"
if not os.path.exists(newpath):
    os.makedirs(newpath)


# ----------------------- [Init Models] --------------------------------
players = [0 for x in range(numPlayers)]
playersGrid = [0 for x in range(numPlayers)]
tasks = [0 for x in range(numTasks)]

# ----------------------- [Init Model Bridges] --------------------------------
playerBridgeGrid = CustomPlayerModelBridge(playersGrid)
playerBridge = CustomPlayerModelBridge(players)

taskBridge = CustomTaskModelBridge(tasks)

# ----------------------- [Init Adaptations] --------------------------------
adaptationGIMME = Adaptation()
adaptationGIMMESA = Adaptation()
adaptationGIMMEOld = Adaptation()

adaptationGIMME1D = Adaptation()
adaptationGIMME2D = Adaptation()
adaptationGIMME5D = Adaptation()
adaptationGIMME6D = Adaptation()


adaptationRandom = Adaptation()
adaptationRandomOld = Adaptation()
adaptationAccurate = Adaptation()


realPersonalities = []
questionnairePersonalities = []

# ----------------------- [Init Log Manager] --------------------------------

# logManager = MongoDBLogManager("mongodb+srv://studyAC1:studyAC1@cluster0-\
# nfksn.mongodb.net/test?retryWrites=true&w=majority")
logManager = CSVLogManager(newpath)



# ----------------------- [Simulation Methods] --------------------------------

def simulateReaction(isBootstrap, playerBridge, currIteration, playerId):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(
		isBootstrap = isBootstrap, 
		playerBridge = playerBridge, 
		state = currState, 
		playerId = playerId, 
		currIteration = currIteration)

	increases = PlayerState(stateType = newState.stateType)
	increases.profile = currState.profile
	increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	playerBridge.setAndSavePlayerStateToGrid(playerId, increases, newState)	
	return increases

def calcReaction(isBootstrap, playerBridge, state, playerId, currIteration):
	personality = playerBridge.getPlayerRealPersonality(playerId)
	numDims = len(personality.dimensions)
	newStateType = 0 if isBootstrap else 1
	newState = PlayerState(
		stateType = newStateType, 
		characteristics = PlayerCharacteristics(
			ability=state.characteristics.ability, 
			engagement=state.characteristics.engagement
			), 
		profile=state.profile)
	newState.characteristics.engagement = 1 - (personality.distanceBetween(state.profile) / math.sqrt(numDims))  #between 0 and 1
	if newState.characteristics.engagement>1:
		breakpoint()
	abilityIncreaseSim = (newState.characteristics.engagement*playerBridge.getBaseLearningRate(playerId))
	newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
	return newState

def executionPhase(isBootstrap, playerBridge, maxNumIterations, startingI, currRun, adaptation):
	if(maxNumIterations <= 0):
		return

	i = startingI
	while(i < maxNumIterations + startingI):

		if adaptation.name == "accurate":
			adaptation.configsGenAlg.updateCurrIteration(i)
		
		print("step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun)+" of "+str(numRuns)+") of algorithm \""+str(adaptation.name)+"\"						", end="\r")
		adaptation.iterate()

		for x in range(numPlayers):
			increases = simulateReaction(isBootstrap, playerBridge, i, x)
			logManager.writeToLog("GIMMESims", "results", 
				{
					"simsID": str(simsID),
					"algorithm": adaptation.name,
					"run": str(currRun),
					"iteration": str(i),
					"playerID": str(x),
					"abilityInc": str(increases.characteristics.ability),
					"engagementInc": str(increases.characteristics.engagement),
					"profDiff": str(playerBridge.getPlayerRealPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)))
				})		
		i+=1


def executeSimulations(maxNumTrainingIterations,firstTrainingI,numRealIterations,firstRealI,\
	playerBridge, taskBridge, adaptation, numInteractionDimensions, estimatorsAccuracy = None, considerExtremePersonalityValues = None):

	estimatorsAccuracy = 0.1 if estimatorsAccuracy == None else estimatorsAccuracy
	considerExtremePersonalityValues = False if considerExtremePersonalityValues == None else considerExtremePersonalityValues

	adaptationName = adaptation.name

	profileTemplate = InteractionsProfile()
	for d in range(numInteractionDimensions):
		profileTemplate.dimensions["dim_"+str(d)] = 0.0


	# create players and tasks
	for x in range(numPlayers):
		playerBridge.registerNewPlayer(
			playerId = int(x), 
			name = "name", 
			currState = PlayerState(profile = profileTemplate.generateCopy().reset()), 
			pastModelIncreasesGrid = PlayerStateGrid(
				interactionsProfileTemplate = profileTemplate.generateCopy().reset(), 
				gridTrimAlg = QualitySortGridTrimAlg(
				# gridTrimAlg = AgeSortGridTrimAlg(
					maxNumModelElements = playerWindow, 
					qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
					), 
				numCells = 1
				), 
			currModelIncreases = PlayerCharacteristics(), personalityEst = profileTemplate.generateCopy().reset(), realPersonality = profileTemplate.generateCopy().reset())
	for x in range(numTasks):
		taskBridge.registerNewTask(
			taskId = int(x), 
			description = "description", 
			minRequiredAbility = random.uniform(0, 1), 
			profile = profileTemplate.generateCopy(), 
			minDuration = datetime.timedelta(minutes=1), 
			difficultyWeight = 0.5, 
			profileWeight = 0.5)



	for r in range(numRuns):
		realPersonalities = []
		questionnairePersonalities = []

		# EPdimensions = [{"dim_0":1,"dim_1":0,"dim_2":0},{"dim_0":0,"dim_1":1,"dim_2":0},{"dim_0":0,"dim_1":0,"dim_2":1}]		
		EPdimensions = [{"dim_0":1,"dim_1":0,"dim_2":0,"dim_3":0},{"dim_0":0,"dim_1":1,"dim_2":0,"dim_3":0},{"dim_0":0,"dim_1":0,"dim_2":1,"dim_3":0},{"dim_0":0,"dim_1":0,"dim_2":0,"dim_3":1}]		
		EPdimensionsAux = EPdimensions.copy()	
		
		playersDimsStr = "players: [\n"	


		for x in range(numPlayers):
			profile = profileTemplate.generateCopy().reset()
			if(considerExtremePersonalityValues):
				if(len(EPdimensionsAux) == 0):
					EPdimensionsAux = EPdimensions.copy()
				profile.dimensions = EPdimensionsAux.pop()
				playersDimsStr += "{"+str(profile.dimensions)+"},\n"
			else:
				for d in range(numInteractionDimensions):
					profile.dimensions["dim_"+str(d)] = random.uniform(0, 1)
			realPersonalities.append(profile)
			realPersonalities[x].normalize()


			profile = profileTemplate.generateCopy().reset()
			currRealPersonality = realPersonalities[x]
			for d in range(numInteractionDimensions):
				profile.dimensions["dim_"+str(d)] = numpy.clip(random.gauss(currRealPersonality.dimensions["dim_"+str(d)], estimatorsAccuracy), 0, 1)
			questionnairePersonalities.append(profile)
			questionnairePersonalities[x].normalize()
		

			# init players including predicted personality
			playerBridge.resetPlayer(x)

			playerBridge.setPlayerPersonalityEst(x, profileTemplate.generateCopy().init())
			# realPersonality = realPersonalities[x]
			# playerBridge.setPlayerRealPersonality(x, realPersonality)

			questionnairePersonality = questionnairePersonalities[x]
			playerBridge.setPlayerRealPersonality(x, questionnairePersonality)
			playerBridge.setBaseLearningRate(x, 0.5)

			playerBridge.getPlayerStateGrid(x).gridTrimAlg.considerStateResidue(False)

		playersDimsStr += "],\n"
		# print(playersDimsStr)


		# executionPhase(True, playerBridge, maxNumTrainingIterations, firstTrainingI, r, adaptation)
		adaptation.bootstrap(maxNumTrainingIterations)

		# change for "real" personality from which the predictions supposidely are based on...
		for x in range(numPlayers):
			playerBridge.resetState(x)

			realPersonality = realPersonalities[x]
			playerBridge.setPlayerRealPersonality(x, realPersonality)
			playerBridge.setBaseLearningRate(x, random.gauss(0.5, 0.05))

			playerBridge.getPlayerStateGrid(x).gridTrimAlg.considerStateResidue(True)

		executionPhase(False, playerBridge, numRealIterations, firstRealI, r, adaptation)





# ----------------------- [Init Algorithms] --------------------------------
regAlg = KNNRegression(playerBridge, 5)

intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0})

simpleConfigsAlgOld = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
# simpleConfigsAlgOld = SimulatedAnnealingConfigsGen(
# 	playerBridge, 
# 	intProfTemplate.generateCopy(), 
# 	regAlg, 
# 	numTestedGroupProfiles = numTestedPlayerProfilesInEst,
# 	numberOfConfigChoices = numberOfConfigChoices, 
# 	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
# 	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMMEOld.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge, 
	configsGenAlg = simpleConfigsAlgOld, 
	name="GIMMEOld"
)

randomOldConfigsAlg = RandomConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup
)
adaptationRandomOld.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = randomOldConfigsAlg,
	name="randomOld"
)



# - - - - - 
intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0})
simpleConfigsAlg = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMME.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = simpleConfigsAlg, 
	name="GIMME"
)


simpleConfigsAlgSA = SimulatedAnnealingConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	temperatureDecay = 2.0 / float(playerWindow), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMMESA.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = simpleConfigsAlgSA, 
	name="GIMME_SA"
)


randomConfigsAlg = RandomConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup
)
adaptationRandom.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = randomConfigsAlg, 
	name="random"
)

accurateConfigsAlg = AccurateConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	simulationFunc = calcReaction, 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)  #needed for currIteration updates
)
adaptationAccurate.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = accurateConfigsAlg,
	name="accurate"
)


# - - - - -
intProfTemplate = InteractionsProfile({"dim_0": 0})
simpleConfigsAlg1D = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMME1D.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge, 
	configsGenAlg = simpleConfigsAlg1D, 
	name="GIMME1D"
)



intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0})
simpleConfigsAlg2D = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMME2D.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge, 
	configsGenAlg = simpleConfigsAlg2D, 
	name="GIMME2D"
)



intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0, "dim_4": 0})
simpleConfigsAlg5D = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMME5D.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge, 
	configsGenAlg = simpleConfigsAlg5D, 
	name="GIMME5D"
)



intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0, "dim_4": 0, "dim_5": 0})
simpleConfigsAlg6D = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = intProfTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMME6D.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge, 
	configsGenAlg = simpleConfigsAlg6D, 
	name="GIMME6D"
)




# ----------------------- [Execute Algorithms] ----------------------------

adaptationGIMME.name = "GIMME"
executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4)

adaptationGIMME.name = "GIMMENoBoot"
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4)


# # adaptationGIMMESA.name = "GIMME_SA"
# # executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# # 	taskBridge, adaptationGIMMESA, 4)

# # adaptationGIMMESA.name = "GIMMENoBoot_SA"
# # executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# # 	taskBridge, adaptationGIMMESA, 4)


executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationAccurate, 4)

executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationRandom, 4)




# Extreme personalities
adaptationGIMME.name = "GIMMEEP"
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4, considerExtremePersonalityValues = True)



# Old vs New comparison
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationRandomOld, 3)

executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMMEOld, 3)


# GIP size comparisons
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME1D, 1)

executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME2D, 2)

executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME5D, 5)

executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME6D, 6)


adaptationGIMME.name = "GIMME_LowAccuracyEst"
executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4, estimatorsAccuracy = 0.2)


adaptationGIMME.name = "GIMME_HighAccuracyEst"
executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4, estimatorsAccuracy = 0.05)

print("Done!                        ", end="\r")


		