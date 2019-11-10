import numpy
import random
import json
import copy

import time

import matplotlib.pyplot as plt
import math


from GIMMECore import *
from ModelMocks import *

from numpy import array

import random
random.seed(time.clock())

numRuns = 4
maxNumIterationsPerRun = 50
numTrainingCyclesPerRun = 0

playerWindow = 30

numPlayers = 23

players = [None for x in range(numPlayers)]
tasks = [None for x in range(20)]



abilityConvergenceEpsilon = 0.02


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

	def resetPlayer(self, playerId):
		players[int(playerId)].currState.reset()
		players[int(playerId)].pastModelIncreasesGrid.reset()
		# print(json.dumps(players[int(playerId)], default=lambda o: o.__dict__, sort_keys=True))

	def savePlayerState(self, playerId, newState):
		players[int(playerId)].currState = newState
		players[int(playerId)].pastModelIncreasesGrid.pushToGrid(newState)

	def getIterationReactions(self, playerId, currIteration):
		return players[int(playerId)].iterationReactions[currIteration]

	def initIterationReactions(self, playerId, reactions):
		players[int(playerId)].iterationReactions = reactions

	def saveIterationReaction(self, playerId, currIteration, reaction):
		players[int(playerId)].iterationReactions[currIteration] = reaction

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



def simulateReaction(currIteration, playerBridge, playerId, intrinsicMeasure):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(copy.deepcopy(currState), playerBridge, playerId, currState.profile, currIteration, intrinsicMeasure)

	newState.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	
	playerBridge.savePlayerState(playerId, newState)

def calcReaction(state, playerBridge, playerId, interactionsProfile, currIteration, intrinsicMeasure):
	# print(len(playerBridge.getPlayerPastModelIncreases(playerId).cells[0]))
	personality = playerBridge.getPlayerPersonality(playerId)
	state.characteristics.engagement = 0.5* (state.characteristics.engagement) + 0.5* (2.0 - intrinsicMeasure.sqrDistanceBetween(interactionsProfile))/2.0

	currTaskReaction = playerBridge.getIterationReactions(playerId, currIteration)
	abilityIncreaseSim = (currTaskReaction * state.characteristics.engagement) #between 0 and 1
	state.characteristics.ability = state.characteristics.ability + abilityIncreaseSim
	
	return state


# create players, tasks and adaptation
playerBridge = CustomPlayerModelBridge()
for x in range(numPlayers):
	playerBridge.registerNewPlayer(int(x), "name", PlayerState(), PlayerStateGrid(1, playerWindow), PlayerCharacteristics(), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), maxNumIterationsPerRun)

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
	playerBridge.setBaseLearningRate(x, numpy.random.uniform(0.2, 0.6))
	playerBridge.initIterationReactions(x, [0]*(maxNumIterationsPerRun+1))
	# playerBridge.initIterationReactions(x, [0]*(numTrainingCyclesPerRun + maxNumIterationsPerRun+1))

	# for p in range(numTrainingCyclesPerRun + numIterationsPerRun+1):
	for p in range(maxNumIterationsPerRun+1):
		playerBridge.saveIterationReaction(x, p, numpy.random.normal(playerBridge.getBaseLearningRate(x), 0.05))



fixedNumberOfPlayersPerGroup = 5
adaptationGIMME10.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=10, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMME.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup,  difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMMEOld.init(KNNRegression(5), RandomConfigsGenOld(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMME1000.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=1000, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMME2000.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=2000, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMMEK1.init(KNNRegression(1), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)

adaptationGIMMEK24.init(KNNRegression(24), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)
adaptationGIMMEK30.init(KNNRegression(30), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)



adaptationRandom.init(KNNRegression(5), RandomConfigsGen(), RandomFitness(), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)

simOptimalFitness = SimulationsOptimalFitness(calcReaction, PlayerCharacteristics(ability=1.0, engagement=0.0)) #needed for currIteration updates
adaptationOptimal.init(KNNRegression(5), RandomConfigsGen(), simOptimalFitness, playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = fixedNumberOfPlayersPerGroup, difficultyWeight = 0.5, profileWeight=0.5)


GIMME10Abilities = [0 for i in range(maxNumIterationsPerRun)]
GIMME10Engagements = [0 for i in range(maxNumIterationsPerRun)]
GIMME10PrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]

GIMMEAbilities = [0 for i in range(maxNumIterationsPerRun)]
GIMMEEngagements = [0 for i in range(maxNumIterationsPerRun)]
GIMMEPrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]
GIMMEGroupSizeFreqs = [0 for i in range(fixedNumberOfPlayersPerGroup)]
GIMMEConfigsSizeFreqs = [0 for i in range(numPlayers)]

GIMMEOldAbilities = [0 for i in range(maxNumIterationsPerRun)]
GIMMEOldEngagements = [0 for i in range(maxNumIterationsPerRun)]
GIMMEOldPrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]
GIMMEOldGroupSizeFreqs = [0 for i in range(fixedNumberOfPlayersPerGroup)]
GIMMEOldConfigsSizeFreqs = [0 for i in range(numPlayers)]


GIMME1000Abilities = [0 for i in range(maxNumIterationsPerRun)]
GIMME1000Engagements = [0 for i in range(maxNumIterationsPerRun)]
GIMME1000PrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]

GIMME2000Abilities = [0 for i in range(maxNumIterationsPerRun)]
GIMME2000Engagements = [0 for i in range(maxNumIterationsPerRun)]
GIMME2000PrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]


GIMMEK1Abilities = [0 for i in range(maxNumIterationsPerRun)]
GIMMEK1Engagements = [0 for i in range(maxNumIterationsPerRun)]
GIMMEK1PrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]

GIMMEK24Abilities = [0 for i in range(maxNumIterationsPerRun)]
GIMMEK24Engagements = [0 for i in range(maxNumIterationsPerRun)]
GIMMEK24PrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]

GIMMEK30Abilities = [0 for i in range(maxNumIterationsPerRun)]
GIMMEK30Engagements = [0 for i in range(maxNumIterationsPerRun)]
GIMMEK30PrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]


randomAbilities = [0 for i in range(maxNumIterationsPerRun)]
randomEngagements = [0 for i in range(maxNumIterationsPerRun)]
randomPrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]


optimalAbilities = [0 for i in range(maxNumIterationsPerRun)]
optimalEngagements = [0 for i in range(maxNumIterationsPerRun)]
optimalPrefProfDiff = [0 for i in range(maxNumIterationsPerRun)]



GIMME10ExecTime = 0.0
GIMMEExecTime = 0.0
GIMMEOldExecTime = 0.0
GIMME1000ExecTime = 0.0
GIMME2000ExecTime = 0.0

GIMMEK1ExecTime = 0.0
GIMMEK24ExecTime = 0.0
GIMMEK30ExecTime = 0.0

randomExecTime = 0.0
optimalExecTime = 0.0

def executionPhase(intrinsicMeasure):
	# for i in range(numIterationsPerRun):
	i=0
	lastCurrAbilityArray = []
	while(i < maxNumIterationsPerRun):
		
		if algType == "optimal":
			simOptimalFitness.updateCurrIteration(i)

		t0 = time.clock()

		print("step (" +str(i)+ " of "+str(maxNumIterationsPerRun)+") of run ("+str(r)+" of "+str(numRuns)+") of algorithm ("+str(algorithmNum)+" of "+str(numAlgorithms)+")						", end="\r")
		iteration = adaptation.iterate()

		t1 = time.clock() - t0
		avgItExecTime += (t1 - t0)/(numRuns) # CPU seconds elapsed (floating point)

		currAbility = 0
		currEngagement = 0
		for x in range(numPlayers):
			simulateReaction(i, playerBridge, x, intrinsicMeasure)
			currCharacteristics = playerBridge.getPlayerCurrCharacteristics(x)
			currAbility += currCharacteristics.ability / numPlayers
			currEngagement += currCharacteristics.engagement / numPlayers

			abilityArray[i] += currAbility / (numRuns)
			engagementArray[i] += currEngagement / (numRuns)
			profDiffArray[i] += playerBridge.getPlayerPersonality(x).distanceBetween(playerBridge.getPlayerCurrProfile(x)) / (numRuns)
	
			lastCurrAbilityArray.append(currAbility)

		if algType == "GIMME":
			print(lastCurrAbilityArray[i] - lastCurrAbilityArray[i-5])
			if(i > 5 and abs(lastCurrAbilityArray[i] - lastCurrAbilityArray[i-5]) < abilityConvergenceEpsilon):
				break

	i+=1

	print(i)

	i += 1.0
	avgItExecTime /= i
	for x in range(maxNumIterationsPerRun):
		abilityArray[x] /= i
		engagementArray[x] /= i
		profDiffArray[x] /= i


def executeSimulations(adaptation, abilityArray, engagementArray, profDiffArray, groupSizeFreqsArray, configSizeFreqsArray, avgItExecTime, algType, algorithmFilename, canExport, algorithmNum, numAlgorithms):
	for r in range(numRuns):
		for x in range(numPlayers):
			playerBridge.resetPlayer(x)

		# if isOptimalRun == True:
		# 	print(json.dumps(players, default=lambda o: o.__dict__, sort_keys=True))
		# 	quit()

		# if(numTrainingCyclesPerRun > 0):
		# 	for i in range(numTrainingCyclesPerRun):
		# 		for x in range(numPlayers):
		# 			simulateReaction(i, playerBridge, x)

		# algorithm simulations simulation 
		executionPhase()

		# algorithm applied to real scenario simulation 
		executionPhase()

	groupSizeFreqs = adaptation.configsGenAlg.groupSizeFreqs
	print(groupSizeFreqs)
	configSizeFreqs = adaptation.configsGenAlg.configSizeFreqs
	print(configSizeFreqs)
	if canExport == True:
		f = open("./simulationResults/"+algorithmFilename+".txt", "w")
		f.write("abilities: "+json.dumps(abilityArray))
		f.write("\nengagements: "+json.dumps(engagementArray))
		f.write("\nprofDiffArray: "+json.dumps(profDiffArray))
		f.close()


executeSimulations(adaptationGIMME,GIMMEAbilities,GIMMEEngagements,GIMMEPrefProfDiff, GIMMEGroupSizeFreqs, GIMMEConfigsSizeFreqs, GIMMEExecTime, "GIMME", "adaptationGIMME", True,  2, 9)



# executeSimulations(adaptationOptimal,optimalAbilities,optimalEngagements,optimalPrefProfDiff, [], [], optimalExecTime, "optimal", "adaptationOptimal", True, 9, 9)
# executeSimulations(adaptationRandom,randomAbilities,randomEngagements,randomPrefProfDiff, [], [], randomExecTime, "random", "adaptationRandom", True,  8, 9)

# executeSimulations(adaptationGIMME10,GIMME10Abilities,GIMME10Engagements,GIMME10PrefProfDiff,GIMME10ExecTime, "GIMME", "adaptationGIMME10", True, 1, 9)

# executeSimulations(adaptationGIMMEOld,GIMMEOldAbilities,GIMMEOldEngagements,GIMMEOldPrefProfDiff, GIMMEOldGroupSizeFreqs, GIMMEOldConfigsSizeFreqs, GIMMEOldExecTime, "GIMME", "adaptationGIMMEOld", True,  2, 9)

# executeSimulations(adaptationGIMME1000,GIMME1000Abilities,GIMME1000Engagements,GIMME1000PrefProfDiff,GIMME1000ExecTime, "GIMME", "adaptationGIMME1000", True, 3, 9)
# executeSimulations(adaptationGIMME2000,GIMME2000Abilities,GIMME2000Engagements,GIMME2000PrefProfDiff,GIMME2000ExecTime, "GIMME", "adaptationGIMME2000", True, 4, 9)
# executeSimulations(adaptationGIMMEK1,GIMMEK1Abilities,GIMMEK1Engagements,GIMMEK1PrefProfDiff,GIMMEK1ExecTime, "GIMME", "adaptationGIMMEK1", True, 5, 9)
# executeSimulations(adaptationGIMMEK24,GIMMEK24Abilities,GIMMEK24Engagements,GIMMEK24PrefProfDiff,GIMMEK24ExecTime, "GIMME", "adaptationGIMMEK24", True, 6, 9)
# executeSimulations(adaptationGIMMEK30,GIMMEK30Abilities,GIMMEK30Engagements,GIMMEK30PrefProfDiff,GIMMEK30ExecTime, "GIMME", "adaptationGIMMEK30", True, 7, 9)


# width = 0.35;

# fixedNumberOfPlayersPerGroupTimesteps=[i for i in range(fixedNumberOfPlayersPerGroup)]

# GIMMEGroupSizeFreqs = numpy.array(GIMMEGroupSizeFreqs)
# GIMMEOldGroupSizeFreqs = numpy.array(GIMMEOldGroupSizeFreqs)

# GIMMEConfigsSizeFreqs = numpy.array(GIMMEConfigsSizeFreqs)
# GIMMEOldConfigsSizeFreqs = numpy.array(GIMMEOldConfigsSizeFreqs)

# plt.subplot(2,1,1)
# plt.bar(fixedNumberOfPlayersPerGroup-width/2, GIMMEGroupSizeFreqs/ sum(GIMMEGroupSizeFreqs), width, align='center', color= "red", alpha=0.5)
# plt.bar(fixedNumberOfPlayersPerGroup+width/2, GIMMEOldGroupSizeFreqs/ sum(GIMMEOldGroupSizeFreqs), width, align='center', color= "green", alpha=0.5)
# plt.xticks(fixedNumberOfPlayersPerGroupTimesteps)
# plt.xlabel("Group Size")
# plt.ylabel("Occurence (%)")


# numPlayersTimesteps=[i for i in range(numPlayers)]

# plt.subplot(2,1,2)
# plt.bar(numPlayers-width/2, GIMMEConfigsSizeFreqs/ sum(GIMMEConfigsSizeFreqs), width, align='center', color= "red", alpha=0.5)
# plt.bar(numPlayers+width/2, GIMMEOldConfigsSizeFreqs/ sum(GIMMEOldConfigsSizeFreqs), width, align='center', color= "green", alpha=0.5)
# plt.xticks(numPlayersTimesteps)
# plt.xlabel("Config. Size")
# plt.ylabel("Occurence (%)")
# plt.show()



timesteps=[i for i in range(maxNumIterationsPerRun)]
# -------------------------------------------------------
plt.plot(timesteps, GIMME10Abilities, label=r'$GIMME 10 Samples (avg. it. exec. time = '+str(GIMME10ExecTime)+')$')
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME 100 Samples (avg. it. exec. time = '+str(GIMMEExecTime)+')$')
plt.plot(timesteps, GIMME1000Abilities, label=r'$GIMME 1000 Samples (avg. it. exec. time = '+str(GIMME1000ExecTime)+')$')
plt.plot(timesteps, GIMME2000Abilities, label=r'$GIMME 2000 Samples (avg. it. exec. time = '+str(GIMME2000ExecTime)+')$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.savefig('./simulationResults/charts/simulationsResultsNSamplesComparison.png')

plt.legend(loc='best')
plt.show()

# -------------------------------------------------------
plt.plot(timesteps, GIMMEK1Abilities, label=r'$GIMME k = 1$')
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME k = 5$')
plt.plot(timesteps, GIMMEK24Abilities, label=r'$GIMME k = 24$')
plt.plot(timesteps, GIMMEK30Abilities, label=r'$GIMME k = 30$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.savefig('./simulationResults/charts/simulationsResultsNSamplesAndNNsComparison.png')

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, GIMMEAbilities, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomAbilities, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalAbilities, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("avg Ability Increase")

plt.savefig('./simulationResults/charts/simulationsResultsAbility_old.png')

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, array(optimalAbilities) - array(GIMMEAbilities), label=r'$GIMME\ strategy$')
plt.plot(timesteps, array(optimalAbilities) - array(randomAbilities), label=r'$Random\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Distance from Optimal avg Ability Increase")

plt.savefig('./simulationResults/charts/simulationsResultsAbility.png')

plt.legend(loc='best')
plt.show()



# -------------------------------------------------------
plt.plot(timesteps, GIMMEEngagements, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomEngagements, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalEngagements, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("Engagement Increase")

plt.savefig('./simulationResults/charts/simulationsResultsEngagement.png')

plt.legend(loc='best')
plt.show()


# -------------------------------------------------------
plt.plot(timesteps, GIMMEPrefProfDiff, label=r'$GIMME\ strategy$')
plt.plot(timesteps, randomPrefProfDiff, label=r'$Random\ strategy$')
plt.plot(timesteps, optimalPrefProfDiff, label=r'$Optimal\ strategy$')

plt.xlabel("Iteration")
plt.ylabel("avg Preference Differences")

plt.savefig('./simulationResults/charts/simulationsResultsProfileDist.png')

plt.legend(loc='best')
plt.show()

