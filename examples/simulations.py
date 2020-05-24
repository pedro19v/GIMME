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
from GIMMECore import *
from ModelMocks import *

from logManager import *

import plotBuilder

random.seed(time.perf_counter())
simsID = seed = random.randrange(sys.maxsize)

numRuns = 10
maxNumTrainingIterations = 20
numRealIterations = 20

preferredNumberOfPlayersPerGroup = 3
numberOfConfigChoices = 500

numTestedPlayerProfilesInEst = 100

playerWindow = 10
numPlayers = 23

startTime = str(datetime.datetime.now())
# newpath = "./simulationResults/" + startTime +" numRuns:" + str(numRuns) + ",maxNumTrainingIterations: " + str(maxNumTrainingIterations) + ", numRealIterations: " + str(numRealIterations)
newpath = "./simulationResults/latestResults/"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# ----------------------- [Log Manager Setup] --------------------------------

logManager = CSVLogManager(newpath)

# ----------------------- [Auxiliary Methods] --------------------------------

def simulateReaction(playerBridge, currIteration, playerId):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(playerBridge, currState, playerId, currState.profile, currIteration)

	increases = PlayerState()
	increases.profile = currState.profile
	increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	playerBridge.setAndSavePlayerStateToGrid(playerId, increases, newState)	
	return increases

def calcReaction(playerBridge, state, playerId, interactionsProfile, currIteration):
	personality = playerBridge.getPlayerRealPersonality(playerId)
	numDims = len(personality.dimensions)
	newState = PlayerState(characteristics = PlayerCharacteristics(ability=state.characteristics.ability, engagement=state.characteristics.engagement), profile=state.profile)
	newState.characteristics.engagement = 1 - (personality.distanceBetween(interactionsProfile) / math.sqrt(numDims))  #between 0 and 1
	if newState.characteristics.engagement>1:
		breakpoint()
	abilityIncreaseSim = (newState.characteristics.engagement*playerBridge.getBaseLearningRate(playerId))
	newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
	return newState

def executionPhase(playerBridge, maxNumIterations, startingI, currRun, adaptation):
	i = startingI
	while(i < maxNumIterations + startingI):

		if adaptation.name == "accurate":
			adaptation.configsGenAlg.updateCurrIteration(i)
		
		# t0 = time.perf_counter()

		print("step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun)+" of "+str(numRuns)+") of algorithm \""+str(adaptation.name)+"\"						", end="\r")
		adaptation.iterate()

		# t1 = time.perf_counter() - t0
		# avgItExecTime += (t1 - t0)/(numRuns) # CPU seconds elapsed (floating point)

		for x in range(numPlayers):
			increases = simulateReaction(playerBridge, i, x)
			logManager.writeToLog("GIMMESims", "results", 
				{
					"simsID": str(simsID),
					"algorithm": adaptation.name,
					"run": str(currRun),
					"iteration": str(i),
					"playerID": str(x),
					"abilityInc": str(increases.characteristics.ability),
					"engagementInc": str(increases.characteristics.engagement),
					# "profDiff": str(playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)))
				})
			# abilityMatrix[i][currRun] += increases.characteristics.ability / numPlayers
			# engagementMatrix[i][currRun] += increases.characteristics.engagement / numPlayers
			# profDiffMatrix[i][currRun] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / numPlayers
		
		i+=1


def executeSimulations(maxNumTrainingIterations,firstTrainingI,numRealIterations,firstRealI,\
	playerBridge, taskBridge, adaptation, numInteractionDimensions, considerExtremePersonalityValues = False):


	adaptationName = adaptation.name


	profileTemplate = InteractionsProfile({})
	for d in range(numInteractionDimensions):
		profileTemplate.dimensions["dim_"+str(d)] = 0.0


	# create players and tasks
	for x in range(numPlayers):
		playerBridge.registerNewPlayer(int(x), "name", PlayerState(profile = profileTemplate.generateCopy().reset()), 
			PlayerStateGrid(profileTemplate.generateCopy(), numCells = 1, maxProfilesPerCell = playerWindow), 
			PlayerCharacteristics(), profileTemplate.generateCopy().reset(), profileTemplate.generateCopy().reset())
	for x in range(20):
		taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), profileTemplate.generateCopy(), 
			datetime.timedelta(minutes=1), 0.5, 0.5)



	for r in range(numRuns):
		realPersonalities = []
		# EPdimensions = [{"dim_0":1,"dim_1":0,"dim_2":0},{"dim_0":0,"dim_1":1,"dim_2":0},{"dim_0":0,"dim_1":0,"dim_2":1}]		
		EPdimensions = [{"dim_0":1,"dim_1":0,"dim_2":0,"dim_3":0},{"dim_0":0,"dim_1":1,"dim_2":0,"dim_3":0},{"dim_0":0,"dim_1":0,"dim_2":1,"dim_3":0},{"dim_0":0,"dim_1":0,"dim_2":0,"dim_3":1}]		
		EPdimensionsAux = EPdimensions.copy()	
		
		playersDimsStr = "players: [\n"	
		
		for x in range(numPlayers):
			profile = profileTemplate.generateCopy()
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

		playersDimsStr += "],\n"
		# print(playersDimsStr)

		questionnairePersonalities = []
		for x in range(numPlayers):
			profile = profileTemplate.generateCopy()
			currRealPersonality = realPersonalities[x]
			for d in range(numInteractionDimensions):
				profile.dimensions["dim_"+str(d)] = numpy.clip(random.gauss(currRealPersonality.dimensions["dim_"+str(d)], 0.1),0,1)
			questionnairePersonalities.append(profile)
			questionnairePersonalities[x].normalize()

		# init players including predicted personality
		for x in range(numPlayers):
			adaptation.configsGenAlg.reset()
			playerBridge.resetPlayer(x)

			playerBridge.setPlayerPersonalityEst(x, intProfTemplate.generateCopy().reset())
			# realPersonality = realPersonalities[x]
			# playerBridge.setPlayerRealPersonality(x, realPersonality)

			questionnairePersonality = questionnairePersonalities[x]
			playerBridge.setPlayerRealPersonality(x, questionnairePersonality)


			# has bootstrap
			# if(maxNumTrainingIterations > 0):
			# 	personality = questionnairePersonalities[x]
			# 	playerBridge.setPlayerPersonalityEst(x, personality)


			playerBridge.setBaseLearningRate(x, random.gauss(0.5, 0.16))


		# breakpoint()

		executionPhase(playerBridge, maxNumTrainingIterations, firstTrainingI, r, adaptation)
	
		# change for "real" personality from which the predictions supposidely are based on...
		for x in range(numPlayers):
			playerBridge.resetState(x)

			realPersonality = realPersonalities[x]
			playerBridge.setPlayerRealPersonality(x, realPersonality)

		executionPhase(playerBridge, numRealIterations, firstRealI, r, adaptation)





players = [0 for x in range(numPlayers)]
playersGrid = [0 for x in range(numPlayers)]
tasks = [0 for x in range(20)]

# ----------------------- [Init Bridges] --------------------------------
playerBridgeGrid = CustomPlayerModelBridge(playersGrid)
playerBridge = CustomPlayerModelBridge(players)

taskBridge = CustomTaskModelBridge(tasks)

# ----------------------- [Init Adaptations] --------------------------------
adaptationGIMME = Adaptation()
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



# ----------------------- [Init Algorithms] --------------------------------
regAlg = KNNRegression(playerBridge, 5)

intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0})

simpleConfigsAlgOld = SimpleConfigsGenVer1(
	playerBridge, 
	intProfTemplate.generateCopy(), 
	regAlg, 
	persEstAlg = SimplePersonalityEstAlg(
		playerBridge, 
		intProfTemplate.generateCopy(), 
		regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
# simpleConfigsAlgOld = SimpleConfigsGenVer2(
# 	playerBridge, 
# 	intProfTemplate.generateCopy(), 
# 	regAlg, 
# 	numTestedGroupProfiles = numTestedPlayerProfilesInEst,
# 	numberOfConfigChoices = numberOfConfigChoices, 
# 	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
# 	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMMEOld.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlgOld, name="GIMMEOld")

randomOldConfigsAlg = RandomConfigsGen(playerBridge, intProfTemplate.generateCopy(), preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationRandomOld.init(playerBridge, taskBridge, configsGenAlg = randomOldConfigsAlg, name="randomOld")

# - - - - - 
intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0})

simpleConfigsAlg = SimpleConfigsGenVer1(
	playerBridge, 
	intProfTemplate.generateCopy(), 
	regAlg, 
	persEstAlg = SimplePersonalityEstAlg(
		playerBridge, 
		intProfTemplate.generateCopy(), 
		regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg, name="GIMME")

randomConfigsAlg = RandomConfigsGen(playerBridge, intProfTemplate.generateCopy(), preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationRandom.init(playerBridge, taskBridge, configsGenAlg = randomConfigsAlg, name="random")

accurateConfigsAlg = AccurateConfigsGen(playerBridge, intProfTemplate.generateCopy(), calcReaction, numberOfConfigChoices=numberOfConfigChoices, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)) #needed for currIteration updates
adaptationAccurate.init(playerBridge, taskBridge, configsGenAlg = accurateConfigsAlg, name="accurate")


# - - - - -

intProfTemplate = InteractionsProfile({"dim_0": 0})

simpleConfigsAlg1D = SimpleConfigsGenVer1(
	playerBridge, 
	intProfTemplate.generateCopy(), 
	regAlg, 
	persEstAlg = SimplePersonalityEstAlg(
		playerBridge, 
		intProfTemplate.generateCopy(), 
		regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME1D.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg1D, name="GIMME1D")



intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0})

simpleConfigsAlg2D = SimpleConfigsGenVer1(
	playerBridge, 
	intProfTemplate.generateCopy(), 
	regAlg, 
	persEstAlg = SimplePersonalityEstAlg(
		playerBridge, 
		intProfTemplate.generateCopy(), 
		regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME2D.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg2D, name="GIMME2D")



intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0, "dim_4": 0})

simpleConfigsAlg5D = SimpleConfigsGenVer1(
	playerBridge, 
	intProfTemplate.generateCopy(), 
	regAlg, 
	persEstAlg = SimplePersonalityEstAlg(
		playerBridge, 
		intProfTemplate.generateCopy(), 
		regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME5D.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg5D, name="GIMME5D")



intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0, "dim_4": 0, "dim_5": 0})

simpleConfigsAlg6D = SimpleConfigsGenVer1(
	playerBridge, 
	intProfTemplate.generateCopy(), 
	regAlg, 
	persEstAlg = SimplePersonalityEstAlg(
		playerBridge, 
		intProfTemplate.generateCopy(), 
		regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME6D.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg6D, name="GIMME6D")




# ----------------------- [Execute Algorithms] ----------------------------



adaptationGIMME.name = "GIMME"
executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4)



adaptationGIMME.name = "GIMMENoBoot"
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, 4)

# # Extreme personalities
# adaptationGIMME.name = "GIMMEEP"
# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME, 4, considerExtremePersonalityValues = True)




# adaptationGIMME.name = "GIMMEEP"
# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMMEOld,
# 	3, considerExtremePersonalityValues = True)




executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationAccurate, 4)


executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationRandom, 4)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	# taskBridge, adaptationRandomOld, 3)


# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMMEOld, 3)


# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME1D, 1)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME2D, 2)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME5D, 5)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME6D, 6)

print("Done!                        ", end="\r")

# print("Generating plot...                        ", end="\r")

# plt = plotBuilder.buildPlot(maxNumTrainingIterations,numRealIterations,
# 	accurateAbilityMeans, randomAbilityMeans, randomOldAbilityMeans,
# 	GIMMEAbilityMeans, GIMMEOldAbilityMeans, 
# 	GIMMENoBootAbilityMeans, GIMMEEPAbilityMeans,

# 	accurateAbilitySTDev, randomAbilitySTDev, randomOldAbilitySTDev,
# 	GIMMEAbilitySTDev, GIMMEOldAbilitySTDev, 
# 	GIMMENoBootAbilitySTDev, GIMMEEPAbilitySTDev,

# 	GIMME1DAbilityMeans, GIMME2DAbilityMeans, GIMME5DAbilityMeans, GIMME6DAbilityMeans,
# 	GIMME1DAbilitySTDev, GIMME2DAbilitySTDev, GIMME5DAbilitySTDev, GIMME6DAbilitySTDev
# 	)

# plt.savefig(newpath+"/charts/chart.png")
# plt.show()

# print("Done!                        ", end="\r")
		