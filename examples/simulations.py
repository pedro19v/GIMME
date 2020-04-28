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

plt.style.use('tableau-colorblind10')
random.seed(time.perf_counter())

numRuns = 30
maxNumTrainingIterations = 20
numRealIterations = 20

playerWindow = 10
numPlayers = 23

startTime = str(datetime.datetime.now())
newpath = "./simulationResults/" + startTime +" numRuns:" + str(numRuns) + ",maxNumTrainingIterations: " + str(maxNumTrainingIterations) + ", numRealIterations: " + str(numRealIterations)
if not os.path.exists(newpath):
    os.makedirs(newpath)
    os.makedirs(newpath+"/charts/")



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
	personality = playerBridge.getPlayerPersonality(playerId)
	newState = PlayerState(characteristics = PlayerCharacteristics(ability=state.characteristics.ability, engagement=state.characteristics.engagement), profile=state.profile)
	newState.characteristics.engagement = (math.sqrt(2.0) - personality.distanceBetween(interactionsProfile)) / math.sqrt(2.0)  #between 0 and 1
	abilityIncreaseSim = (newState.characteristics.engagement*playerBridge.getBaseLearningRate(playerId))
	newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
	return newState

def executionPhase(playerBridge, maxNumIterations, startingI, currRun, adaptation, \
	abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, \
	canExport):
	i = startingI
	
	if i==0 and (adaptation.name == "GIMME" or adaptation.name == "GIMMENoBoot" or adaptation.name == "GIMMEOld"):
		adaptation.configsGenAlg.areAllPlayersInited(False)
	
	while(i < maxNumIterations + startingI):
		if adaptation.name == "accurate":
			adaptation.configsGenAlg.updateCurrIteration(i)
		
		t0 = time.perf_counter()

		print("step (" +str(i - startingI)+ " of "+str(maxNumIterations)+") of run ("+str(currRun)+" of "+str(numRuns)+") of algorithm \""+str(adaptation.name)+"\"						", end="\r")
		adaptation.iterate()

		t1 = time.perf_counter() - t0
		avgItExecTime += (t1 - t0)/(numRuns) # CPU seconds elapsed (floating point)

		for x in range(numPlayers):
			increases = simulateReaction(playerBridge, i, x)
			abilityMatrix[i][currRun] += increases.characteristics.ability / numPlayers
			engagementMatrix[i][currRun] += increases.characteristics.engagement / numPlayers
			profDiffMatrix[i][currRun] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / numPlayers
		i+=1

		if adaptation.name == "GIMME" or adaptation.name == "GIMMENoBoot" or adaptation.name == "GIMMEOld":
			adaptation.configsGenAlg.areAllPlayersInited(True)



def executeSimulations(maxNumTrainingIterations,firstTrainingI,numRealIterations,firstRealI,\
	playerBridge, taskBridge, adaptation, \
	abilityMean, abilitySTDev, engagementMean, engagementSTDev, profDiffMean, profDiffSTDev, avgItExecTime,\
	canExport, numInteractionDimensions):


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
		if adaptationName == "GIMMEGrid":
			playerBridge.registerNewPlayer(int(x), "name", PlayerState(creationTime = time.time(), profile = profileTemplate.generateCopy()), PlayerStateGrid(profileTemplate.generateCopy(), numCells = 5, maxProfilesPerCell = 2), PlayerCharacteristics(), profileTemplate.generateCopy())
		else:
			playerBridge.registerNewPlayer(int(x), "name", PlayerState(creationTime = time.time(), profile = profileTemplate.generateCopy()), PlayerStateGrid(profileTemplate.generateCopy(), numCells = 1, maxProfilesPerCell = playerWindow), PlayerCharacteristics(), profileTemplate.generateCopy())
	for x in range(20):
		taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), profileTemplate.generateCopy(), datetime.timedelta(minutes=1), 0.5, 0.5)


	for r in range(numRuns):
		realPersonalities = []
		for x in range(numPlayers):
			profile = profileTemplate.generateCopy()
			for d in range(numInteractionDimensions):
				profile.dimensions["dim_"+str(d)] = random.uniform(0, 1)
			realPersonalities.append(profile)
			realPersonalities[x].normalize()

		questionnairePersonalities = []
		for x in range(numPlayers):
			profile = profileTemplate.generateCopy()
			currRealPersonality = realPersonalities[x]
			for d in range(numInteractionDimensions):
				profile.dimensions["dim_"+str(d)] = numpy.clip(random.gauss(currRealPersonality.dimensions["dim_"+str(d)], 0.2),0,1)
			questionnairePersonalities.append(profile)
			questionnairePersonalities[x].normalize()

		# init players including predicted personality
		for x in range(numPlayers):
			adaptation.configsGenAlg.reset()
			playerBridge.resetPlayer(x)
			personality = questionnairePersonalities[x]
			# personality.normalize()
			playerBridge.setPlayerPersonality(x, personality)
			playerBridge.setBaseLearningRate(x, random.gauss(0.5, 0.16))

		executionPhase(playerBridge, maxNumTrainingIterations, firstTrainingI, r, adaptation, abilityMatrix, engagementMatrix, profDiffMatrix, avgItExecTime, canExport)
		
		# change for "real" personality from which the predictions supposidely are based on...
		for x in range(numPlayers):
			playerBridge.resetPlayer(x)
			predictedPersonality = playerBridge.getPlayerPersonality(x)
			realPersonality = realPersonalities[x]
			# realPersonality.normalize()
			# print(json.dumps(realPersonality, default= lambda o: o.__dict__, sort_keys=True))
			# print("---")
			playerBridge.setPlayerPersonality(x, realPersonality)

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
adaptationGIMMEOld = Adaptation()


adaptationRandom = Adaptation()
adaptationRandomOld = Adaptation()
adaptationOptimal = Adaptation()


realPersonalities = []
questionnairePersonalities = []


# ----------------------- [Init Algorithms] --------------------------------
preferredNumberOfPlayersPerGroup = 4

# - - - - - 
intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0})

simpleConfigsAlgOld = SimpleConfigsGen(playerBridge, intProfTemplate.generateCopy(), regAlg = KNNRegression(playerBridge, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMMEOld.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlgOld, name="GIMMEOld")

randomOldConfigsAlg = RandomConfigsGen(playerBridge, intProfTemplate.generateCopy(), preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationRandomOld.init(playerBridge, taskBridge, configsGenAlg = randomOldConfigsAlg, name="randomOld")

# - - - - - 
intProfTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0, "dim_2": 0, "dim_3": 0})

simpleConfigsAlg = SimpleConfigsGen(playerBridge, intProfTemplate.generateCopy(), regAlg = KNNRegression(playerBridge, 5), numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5))
adaptationGIMME.init(playerBridge, taskBridge, configsGenAlg = simpleConfigsAlg, name="GIMME")

randomConfigsAlg = RandomConfigsGen(playerBridge, intProfTemplate.generateCopy(), preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup)
adaptationRandom.init(playerBridge, taskBridge, configsGenAlg = randomConfigsAlg, name="random")

accurateConfigsAlg = AccurateConfigsGen(playerBridge, intProfTemplate.generateCopy(), calcReaction, numberOfConfigChoices=100, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, qualityWeights = PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates
adaptationOptimal.init(playerBridge, taskBridge, configsGenAlg = accurateConfigsAlg, name="accurate")




# ----------------------- [Create Arrays] --------------------------------

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


optimalAbilityMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalEngagementMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalProfDiffMeans = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalAbilitySTDev = [0 for y in range(maxNumTrainingIterations + numRealIterations)]
optimalEngagementSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalProfDiffSTDev = [0  for y in range(maxNumTrainingIterations + numRealIterations)]
optimalExecTime = 0.0


# ----------------------- [Execute Algorithms] ----------------------------


executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationOptimal, optimalAbilityMeans, optimalAbilitySTDev, optimalEngagementMeans, optimalEngagementSTDev, 
	optimalProfDiffMeans, optimalProfDiffSTDev, optimalExecTime, True, 4)

executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationRandom, randomAbilityMeans, randomAbilitySTDev, randomEngagementMeans, randomEngagementSTDev, 
	randomProfDiffMeans, randomProfDiffSTDev, randomExecTime, True, 4)
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationRandomOld, randomOldAbilityMeans, randomOldAbilitySTDev, randomOldEngagementMeans, randomOldEngagementSTDev, 
	randomOldProfDiffMeans, randomOldProfDiffSTDev, randomOldExecTime, True, 3)


executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMMEOld, GIMMEOldAbilityMeans, GIMMEOldAbilitySTDev, 
	GIMMEOldEngagementMeans, GIMMEOldEngagementSTDev, 
	GIMMEOldProfDiffMeans, GIMMEOldProfDiffSTDev, GIMMEOldExecTime, True, 3)
executeSimulations(maxNumTrainingIterations, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, GIMMEAbilityMeans, GIMMEAbilitySTDev, GIMMEEngagementMeans, GIMMEEngagementSTDev, 
	GIMMEProfDiffMeans, GIMMEProfDiffSTDev, GIMMEExecTime, True, 4)


adaptationGIMME.name = "GIMMENoBoot"
executeSimulations(0, 0, numRealIterations, maxNumTrainingIterations, playerBridge, 
	taskBridge, adaptationGIMME, GIMMENoBootAbilityMeans, GIMMENoBootAbilitySTDev, 
	GIMMENoBootEngagementMeans, GIMMENoBootEngagementSTDev, GIMMENoBootProfDiffMeans, GIMMENoBootProfDiffSTDev, GIMMENoBootExecTime, True, 4)



print("Done!                        ", end="\r")


print("Generating results...                        ", end="\r")
import numpy as np 
import seaborn as sns
# ----------------------- [Generate Plots] --------------------------------
sns.set_palette(sns.color_palette("colorblind"))

timesteps=[i+1 for i in range(maxNumTrainingIterations + numRealIterations)]
timestepsReal=[i+1 for i in range(numRealIterations)]
convValue=[1.0 for i in range(maxNumTrainingIterations + numRealIterations)]
empHighestValue=[max(optimalAbilityMeans) for i in range(maxNumTrainingIterations + numRealIterations)]
totalMin = min(min(randomAbilityMeans[maxNumTrainingIterations:]),min(GIMMEAbilityMeans),min(GIMMEOldAbilityMeans[maxNumTrainingIterations:]),min(optimalAbilityMeans[maxNumTrainingIterations:]))
totalMax = max(max(randomAbilityMeans[maxNumTrainingIterations:]),max(GIMMEAbilityMeans),max(GIMMEOldAbilityMeans[maxNumTrainingIterations:]),max(optimalAbilityMeans[maxNumTrainingIterations:]))

plt.rcParams.update({'font.size': 22})

plt.xticks(np.arange(1, numRealIterations+1, step=1.0), fontsize=30)
plt.yticks(fontsize=30)


plt.errorbar(timestepsReal, GIMMEAbilityMeans[maxNumTrainingIterations:], GIMMEAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="Bootstrapped GIMME")
plt.errorbar(timestepsReal, GIMMENoBootAbilityMeans[maxNumTrainingIterations:], GIMMENoBootAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="GIMME")
plt.errorbar(timestepsReal, randomAbilityMeans[maxNumTrainingIterations:], randomAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="Random")
plt.errorbar(timestepsReal, GIMMEOldAbilityMeans[maxNumTrainingIterations:], GIMMEOldAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="GIMME (old GIPs)")
plt.errorbar(timestepsReal, randomOldAbilityMeans[maxNumTrainingIterations:], randomOldAbilitySTDev[maxNumTrainingIterations:], marker='s', capsize=5.0, alpha=0.5, linewidth=3, elinewidth=2, label="Random (old GIPs)")
plt.plot(timestepsReal, empHighestValue[maxNumTrainingIterations:], linestyle= "--", linewidth=3, label="\"Perfect Information\" upper bound")
plt.xlabel("Iteration", fontsize=40)
plt.ylabel("avg. Ability Increase", fontsize=40)
plt.legend(loc='best', fontsize=29)

plt.savefig(newpath+"/charts/chart.png")
plt.show()

print("Done!                        ", end="\r")
		