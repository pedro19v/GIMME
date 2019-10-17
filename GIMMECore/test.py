import numpy
import random

from GIMMECore import *
from ModelMocks import *


players = [None for x in range(100)]
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
	
	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		players[int(playerId)] = PlayerModelMock(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality)	

	def savePlayerState(self, playerId, newState):
		players[int(playerId)].pastModelIncreasesGrid.pushToGrid(stateIncreases)

	def resetPlayer(self, playerId):
		return 0


	def getSelectedPlayerIds(self):
		return [int(i) for i in range(100)]


	def getPlayerName(self, playerId):
		return players[int(playerId)].name

	def getPlayerCurrState(self,  playerId):
		return players[int(playerId)].currState

	def getPlayerCurrProfile(self,  playerId):
		return players[int(playerId)].currState.profile

	def getPlayerPastModelIncreases(self, playerId):
		return players[int(playerId)].pastModelIncreasesGrid.cells

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



playerBridge = CustomPlayerModelBridge()
for x in range(100):
	playerBridge.registerNewPlayer(int(x), "name", PlayerState(), PlayerStateGrid(1, 30), PlayerCharacteristics(), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)))

taskBridge = CustomTaskModelBridge()
for x in range(20):
	taskBridge.registerNewTask(int(x), "description", random.uniform(0, 1), InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), 0.5, 0.5)

adaptation = Adaptation()
adaptation.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=50, maxNumberOfPlayersPerGroup = 5, difficultyWeight = 0.5, profileWeight=0.5)

iteration = adaptation.iterate()
for i in range(len(iteration.groups)):
	currGroup = iteration.groups[i]
	print(currGroup.__dict__)
