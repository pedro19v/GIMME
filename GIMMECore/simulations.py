import numpy
import random
import json
import copy


from GIMMECore import *
from ModelMocks import *

numRuns = 100
numIterationsPerRun = 30
numTrainingCyclesPerRun = 30

playerWindow = 30

numPlayers = 23

players = [None for x in range(numPlayers)]
tasks = [None for x in range(20)]

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

	def savePlayerState(self, playerId, newState):
		players[int(playerId)].currState = newState
		players[int(playerId)].pastModelIncreasesGrid.pushToGrid(newState)

	def getIterationReactions(self, playerId, currIteration):
		return players[int(playerId)].iterationReactions[currIteration]

	def initIterationReactions(self, playerId, reactions):
		players[int(playerId)].iterationReactions = reactions

	def saveIterationReaction(self, playerId, currIteration, reaction):
		players[int(playerId)].iterationReactions[currIteration] = reaction

	def saveInherentPreference(self, playerId, ip):
		players[int(playerId)].inherentPreference = ip

	def getInherentPreference(self, playerId):
		return players[int(playerId)].inherentPreference

	def saveBaseLearningRate(self, playerId, blr):
		players[int(playerId)].baseLearningRate = blr

	def getBaseLearningRate(self, playerId):
		return players[int(playerId)].baseLearningRate

	def resetPlayer(self, playerId):
		return 0


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
	currState = copy.deepcopy(playerBridge.getPlayerCurrState(playerId))
	increases = calcReaction(currState, playerBridge, playerId, currIteration)

	increases.characteristics = PlayerCharacteristics(ability=(currState.characteristics.ability - increases.characteristics.ability), engagement=currState.characteristics.engagement)
	playerBridge.savePlayerState(playerId, increases)

def calcReaction(state, playerBridge, playerId, currIteration):
	currProfile = copy.deepcopy(state.profile)
	inherentPreference = playerBridge.getInherentPreference(playerId)

	state.characteristics.engagement = 0.5* (state.characteristics.engagement) + 0.5* (1.0 - inherentPreference.distanceBetween(state.profile))

	currTaskReaction = playerBridge.getIterationReactions(playerId, currIteration)
	abilityIncreaseSim = (currTaskReaction * state.characteristics.engagement); #between 0 and 1
	state.characteristics.ability += abilityIncreaseSim;
	return state


# create players, tasks and adaptation
playerBridge = CustomPlayerModelBridge()
for x in range(numPlayers):
	playerBridge.registerNewPlayer(int(x), "name", PlayerState(), PlayerStateGrid(1, playerWindow), PlayerCharacteristics(), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), numIterationsPerRun)

taskBridge = CustomTaskModelBridge()
for x in range(20):
	taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), 0.5, 0.5)

adaptation = Adaptation()



# init players
for x in range(numPlayers):
	playerBridge.saveInherentPreference(x, InteractionsProfile(K_i=numpy.random.uniform(0, 1), K_cp=numpy.random.uniform(0, 1), K_mh=numpy.random.uniform(0, 1), K_pa=numpy.random.uniform(0, 1)))
	playerBridge.saveBaseLearningRate(x, numpy.random.uniform(0.2, 0.6))
	playerBridge.initIterationReactions(x, [0]*numIterationsPerRun)

	for p in range(playerWindow):
		playerBridge.saveIterationReaction(x, p, numpy.random.normal(playerBridge.getBaseLearningRate(x), 0.05))


adaptation.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=100, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)


for r in range(numRuns):

	for i in range(numTrainingCyclesPerRun):
		for x in range(numPlayers):
			simulateReaction(i, playerBridge, x) 

	for i in range(numIterationsPerRun):
		iteration = adaptation.iterate()

		for x in range(numPlayers):
			simulateReaction(i, playerBridge, x) 


