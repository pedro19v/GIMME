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

import plotBuilder


random.seed(time.perf_counter())

numRuns = 300
maxNumTrainingIterations = 20
numRealIterations = 20

preferredNumberOfPlayersPerGroup = 3
numberOfConfigChoices = 500

numTestedPlayerProfilesInEst = 100

playerWindow = 10
numPlayers = 9

startTime = str(datetime.datetime.now())
newpath = "./simulationResults/" + startTime +" numRuns:" + str(numRuns) + ",maxNumTrainingIterations: " + str(maxNumTrainingIterations) + ", numRealIterations: " + str(numRealIterations)
if not os.path.exists(newpath):
    os.makedirs(newpath)
    os.makedirs(newpath+"/charts/")


f = open(newpath+"/results.py", "a")
f.write("maxNumTrainingIterations = "+ str(maxNumTrainingIterations)+"\n");
f.write("numRealIterations = "+ str(numRealIterations)+"\n");
f.close()

f2 = open("./latestResults.py", "w")
f2.write("maxNumTrainingIterations = "+ str(maxNumTrainingIterations)+"\n");
f2.write("numRealIterations = "+ str(numRealIterations)+"\n");
f2.close()

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

def executionPhase(playerBridge, maxNumIterations, startingI, currRun, adaptation, \
	abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, \
	canExport):
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
			abilityMatrix[i][currRun] += increases.characteristics.ability / numPlayers
			# engagementMatrix[i][currRun] += increases.characteristics.engagement / numPlayers
			# profDiffMatrix[i][currRun] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / numPlayers
		i+=1


def executeSimulations(maxNumTrainingIterations,firstTrainingI,numRealIterations,firstRealI,\
	playerBridge, taskBridge, adaptation, \
	abilityMean, abilitySTDev, engagementMean, engagementSTDev, profDiffMean, profDiffSTDev, avgItExecTime,\
	numInteractionDimensions, canExport = True, considerExtremePersonalityValues = False):


	totalNumIterations = len(abilityMean) #assumption that the total number of iterations is given by the size of the ability results array...

	abilityMatrix = [[0 for i in range(numRuns)] for y in range(len(abilityMean))]
	engagementMatrix = [[0 for i in range(numRuns)] for y in range(len(engagementMean))]
	profDiffMatrix = [[0 for i in range(numRuns)] for y in range(len(profDiffMean))]

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

		executionPhase(playerBridge, maxNumTrainingIterations, firstTrainingI, r, adaptation, abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, canExport)
	
		# change for "real" personality from which the predictions supposidely are based on...
		for x in range(numPlayers):
			playerBridge.resetState(x)

			realPersonality = realPersonalities[x]
			playerBridge.setPlayerRealPersonality(x, realPersonality)

		executionPhase(playerBridge, numRealIterations, firstRealI, r, adaptation, abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, canExport)


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

		if(numRuns > 1):
			abilitySTDev[i] = math.sqrt(abs(abilitySTDev[i] - abilityMean[i]**2) * (numRuns/(numRuns - 1)))
			engagementSTDev[i] = math.sqrt(abs(engagementSTDev[i] - engagementMean[i]**2) * (numRuns/(numRuns - 1)))
			profDiffSTDev[i] = math.sqrt(abs(profDiffSTDev[i] - profDiffMean[i]**2) * (numRuns/(numRuns - 1)))
	
	groupSizeFreqs = adaptation.configsGenAlg.groupSizeFreqs
	configSizeFreqs = adaptation.configsGenAlg.configSizeFreqs

	if canExport == True:
		f = open(newpath+"/results.py", "a")
		f.write(adaptationName+"AbilityMeans = "+json.dumps(abilityMean)+"\n")
		f.write(adaptationName+"AbilitySTDev = "+json.dumps(abilitySTDev)+"\n")
		f.write(adaptationName+"EngagementMeans = "+json.dumps(engagementMean)+"\n")
		f.write(adaptationName+"EngagementSTDev = "+json.dumps(engagementSTDev)+"\n")
		f.write(adaptationName+"ProfDiffMeans = "+json.dumps(profDiffMean)+"\n")
		f.write(adaptationName+"ProfDiffSTDev = "+json.dumps(profDiffSTDev)+"\n")
		f.write("\n")
		f.close()

		f2 = open("./latestResults.py", "a")
		f2.write(adaptationName+"AbilityMeans = "+json.dumps(abilityMean)+"\n")
		f2.write(adaptationName+"AbilitySTDev = "+json.dumps(abilitySTDev)+"\n")
		f2.write(adaptationName+"EngagementMeans = "+json.dumps(engagementMean)+"\n")
		f2.write(adaptationName+"EngagementSTDev = "+json.dumps(engagementSTDev)+"\n")
		f2.write(adaptationName+"ProfDiffMeans = "+json.dumps(profDiffMean)+"\n")
		f2.write(adaptationName+"ProfDiffSTDev = "+json.dumps(profDiffSTDev)+"\n")
		f2.write("\n")
		f2.close()







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
# - - - - - 

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

# ----------------------- [Create Arrays] --------------------------------

GIMMEEPAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPExecTime = 0.0


GIMMEOldAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldExecTime = 0.0


GIMMENoBootAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootExecTime = 0.0

GIMMEAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEExecTime = 0.0

GIMMEGridAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridExecTime = 0.0

GIMMEEvAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
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

randomOldAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldExecTime = 0.0


accurateAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
accurateEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateExecTime = 0.0


GIMME2DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DExecTime = 0.0


GIMME1DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DExecTime = 0.0


GIMME5DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DExecTime = 0.0


GIMME6DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DExecTime = 0.0



adaptationInitStr = """
GIMMEEPAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEPExecTime = 0.0


GIMMEOldAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEOldExecTime = 0.0


GIMMENoBootAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMENoBootExecTime = 0.0

GIMMEAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEExecTime = 0.0

GIMMEGridAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMMEGridExecTime = 0.0

GIMMEEvAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
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

randomOldAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
randomOldExecTime = 0.0


accurateAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
accurateEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
accurateExecTime = 0.0


GIMME2DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME2DExecTime = 0.0


GIMME1DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME1DExecTime = 0.0


GIMME5DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME5DExecTime = 0.0


GIMME6DAbilityMeans = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
GIMME6DExecTime = 0.0
	"""



f = open(newpath+"/results.py", "a")
f.write(adaptationInitStr)
f.write("\n")
f.close()

f2 = open("./latestResults.py", "a")
f2.write(adaptationInitStr)
f2.write("\n")
f2.close()


# ----------------------- [Execute Algorithms] ----------------------------



adaptationGIMME.name = "GIMME"
executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, GIMMEAbilityMeans, GIMMEAbilitySTDev, GIMMEEngagementMeans, GIMMEEngagementSTDev, 
	GIMMEProfDiffMeans, GIMMEProfDiffSTDev, GIMMEExecTime, 4)




adaptationGIMME.name = "GIMMENoBoot"
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, GIMMENoBootAbilityMeans, GIMMENoBootAbilitySTDev, 
	GIMMENoBootEngagementMeans, GIMMENoBootEngagementSTDev, GIMMENoBootProfDiffMeans, GIMMENoBootProfDiffSTDev,
	GIMMENoBootExecTime, 4)

# # Extreme personalities
# adaptationGIMME.name = "GIMMEEP"
# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME, GIMMEEPAbilityMeans, GIMMEEPAbilitySTDev, 
# 	GIMMEEPEngagementMeans, GIMMEEPEngagementSTDev, GIMMEEPProfDiffMeans, GIMMEEPProfDiffSTDev, GIMMEEPExecTime,
# 	4, considerExtremePersonalityValues = True)




# adaptationGIMME.name = "GIMMEEP"
# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMMEOld, GIMMEEPAbilityMeans, GIMMEEPAbilitySTDev, 
# 	GIMMEEPEngagementMeans, GIMMEEPEngagementSTDev, GIMMEEPProfDiffMeans, GIMMEEPProfDiffSTDev, GIMMEEPExecTime,
# 	3, considerExtremePersonalityValues = True)




executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationAccurate, accurateAbilityMeans, accurateAbilitySTDev, accurateEngagementMeans, accurateEngagementSTDev, 
	accurateProfDiffMeans, accurateProfDiffSTDev, accurateExecTime, 4)


executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationRandom, randomAbilityMeans, randomAbilitySTDev, randomEngagementMeans, randomEngagementSTDev, 
	randomProfDiffMeans, randomProfDiffSTDev, randomExecTime, 4)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	# taskBridge, adaptationRandomOld, randomOldAbilityMeans, randomOldAbilitySTDev, randomOldEngagementMeans, randomOldEngagementSTDev, 
	# randomOldProfDiffMeans, randomOldProfDiffSTDev, randomOldExecTime, 3)


# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMMEOld, GIMMEOldAbilityMeans, GIMMEOldAbilitySTDev, 
# 	GIMMEOldEngagementMeans, GIMMEOldEngagementSTDev, 
# 	GIMMEOldProfDiffMeans, GIMMEOldProfDiffSTDev, GIMMEOldExecTime, 3)


# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME1D, GIMME1DAbilityMeans, GIMME1DAbilitySTDev, GIMME1DEngagementMeans, GIMME1DEngagementSTDev, 
# 	GIMME1DProfDiffMeans, GIMME1DProfDiffSTDev, GIMME1DExecTime, 1)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME2D, GIMME2DAbilityMeans, GIMME2DAbilitySTDev, GIMME2DEngagementMeans, GIMME2DEngagementSTDev, 
# 	GIMME2DProfDiffMeans, GIMME2DProfDiffSTDev, GIMME2DExecTime, 2)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME5D, GIMME5DAbilityMeans, GIMME5DAbilitySTDev, GIMME5DEngagementMeans, GIMME5DEngagementSTDev, 
# 	GIMME5DProfDiffMeans, GIMME5DProfDiffSTDev, GIMME5DExecTime, 5)

# executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
# 	taskBridge, adaptationGIMME6D, GIMME6DAbilityMeans, GIMME6DAbilitySTDev, GIMME6DEngagementMeans, GIMME6DEngagementSTDev, 
# 	GIMME6DProfDiffMeans, GIMME6DProfDiffSTDev, GIMME6DExecTime, 6)

print("Done!                        ", end="\r")
print("Generating plot...                        ", end="\r")

plt = plotBuilder.buildPlot(maxNumTrainingIterations,numRealIterations,
	accurateAbilityMeans, randomAbilityMeans, randomOldAbilityMeans,
	GIMMEAbilityMeans, GIMMEOldAbilityMeans, 
	GIMMENoBootAbilityMeans, GIMMEEPAbilityMeans,

	accurateAbilitySTDev, randomAbilitySTDev, randomOldAbilitySTDev,
	GIMMEAbilitySTDev, GIMMEOldAbilitySTDev, 
	GIMMENoBootAbilitySTDev, GIMMEEPAbilitySTDev,

	GIMME1DAbilityMeans, GIMME2DAbilityMeans, GIMME5DAbilityMeans, GIMME6DAbilityMeans,
	GIMME1DAbilitySTDev, GIMME2DAbilitySTDev, GIMME5DAbilitySTDev, GIMME6DAbilitySTDev
	)

plt.savefig(newpath+"/charts/chart.png")
plt.show()

print("Done!                        ", end="\r")
		