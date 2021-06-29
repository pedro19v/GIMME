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



print("------------------------------------------")
print("-----                                -----")
print("-----       GIMME API EXAMPLE        -----")
print("-----                                -----")
print("-----      (SIMULATING A CLASS)      -----")
print("-----                                -----")
print("------------------------------------------")


print("------------------------------------------")
print("NOTE: This example tests several group organization algorithms types.")
print("For more details, consult the source code.")
print("------------------------------------------")

random.seed(time.perf_counter())
simsID = seed = random.randrange(sys.maxsize)

numRuns = 25
maxNumTrainingIterations = 20
numRealIterations = 20

preferredNumberOfPlayersPerGroup = 4
numberOfConfigChoices = 100

numTestedPlayerProfilesInEst = 500

playerWindow = 10
numPlayers = 24

numTasks = 1

startTime = str(datetime.datetime.now())
newpath = "./simulationResults/latestResults/"
if not os.path.exists(newpath):
    os.makedirs(newpath)


# ----------------------- [Init Models] --------------------------------
print("Initing mocked models...")

players = [0 for x in range(numPlayers)]
playersGrid = [0 for x in range(numPlayers)]
tasks = [0 for x in range(numTasks)]

# ----------------------- [Init Model Bridges] --------------------------------
print("Initing model bridges...")

playerBridgeGrid = CustomPlayerModelBridge(playersGrid)
playerBridge = CustomPlayerModelBridge(players)

taskBridge = CustomTaskModelBridge(tasks)

# ----------------------- [Init Adaptations] --------------------------------
adaptationGIMME = Adaptation()
adaptationEvl = Adaptation()


adaptationRandom = Adaptation()
adaptationAccurate = Adaptation()


realPersonalities = []
questionnairePersonalities = []

# ----------------------- [Init Log Manager] --------------------------------
print("Initing .csv log manager...")
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
		
		print("Performing step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun+1)+" of "+str(numRuns)+") of algorithm \""+str(adaptation.name)+"\"...                                                             ", end="\r")
		adaptation.iterate()

		for x in range(numPlayers):
			increases = simulateReaction(isBootstrap, playerBridge, i, x)
			logManager.writeToLog("GIMMESims", "resultsEvl", 
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
			pastModelIncreasesGrid = PlayerStatesDataFrame(
				interactionsProfileTemplate = profileTemplate.generateCopy().reset(), 
				gridTrimAlg = QualitySortPlayerDataTrimAlg(
				# gridTrimAlg = AgeSortPlayerDataTrimAlg(
					maxNumModelElements = playerWindow, 
					qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
					)
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

		EPdimensions = [{"dim_0":1,"dim_1":0,},{"dim_0":0,"dim_1":1}]		
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

			playerBridge.getPlayerStatesDataFrame(x).gridTrimAlg.considerStateResidue(False)

		playersDimsStr += "],\n"
		# print(playersDimsStr)


		if(maxNumTrainingIterations > 0):		
			adaptation.bootstrap(maxNumTrainingIterations)

		# change for "real" personality from which the predictions supposidely are based on...
		for x in range(numPlayers):
			playerBridge.resetState(x)

			realPersonality = realPersonalities[x]
			playerBridge.setPlayerRealPersonality(x, realPersonality)
			playerBridge.setBaseLearningRate(x, random.gauss(0.5, 0.05))

			playerBridge.getPlayerStatesDataFrame(x).gridTrimAlg.considerStateResidue(True)
		
		if r > 0:
			adaptation.configsGenAlg.reset()

		executionPhase(False, playerBridge, numRealIterations, firstRealI, r, adaptation)





# ----------------------- [Init Algorithms] --------------------------------
print("Initing algorithms...")

regAlg = KNNRegression(playerModelBridge = playerBridge, numberOfNNs = 5)

# - - - - - 
intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0})

evolutionaryConfigsAlg = EvolutionaryConfigsGenDEAP(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
	regAlg = regAlg, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5),
	initialPopulationSize = 200, 
	numberOfEvolutionsPerIteration = 50, 
	
	probOfCross = 0.7, 
	probOfMutation = 1.0,

	probOfMutationConfig = 0.05, 
	probOfMutationGIPs = 0.05, 
	
	numFitSurvivors = 10
)
# evolutionaryConfigsAlg = EvolutionaryConfigsGenDEAP(
# 	playerModelBridge = playerBridge, 
# 	interactionsProfileTemplate = intProfTemplate.generateCopy(), 
# 	regAlg = regAlg, 
# 	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
# 	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5),
# 	initialPopulationSize = 200, 
# 	numberOfEvolutionsPerIteration = 100, 
	
# 	probOfCross = 0.7, 
# 	probOfMutation = 1.0,

# 	probOfMutationConfig = 0.05, 
# 	probOfMutationGIPs = 0.05, 
	
# 	numFitSurvivors = 10
# )
adaptationEvl.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = evolutionaryConfigsAlg, 
	name="GIMME"
)

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


# ----------------------- [Execute Algorithms] ----------------------------
input("<<< All ready! Press any key to start. >>>")


adaptationEvl.name = "GIMME_Evl"
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, 
	playerBridge, taskBridge, adaptationEvl, 2)

# adaptationGIMME.name = "GIMME"
# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, 
# 	playerBridge, taskBridge, adaptationGIMME, 2)

# adaptationRandom.name = "Random"
# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations,
# 	playerBridge, taskBridge, adaptationRandom, 2)



print("Done!                        ", end="\r")


		