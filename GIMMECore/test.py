import numpy

from Adaptation import Adaptation
from AlgDefStructs.RegressionAlg import *
from AlgDefStructs.ConfigsGenAlg import *
from AlgDefStructs.FitnessAlg import *

from Player.PlayerStructs import PlayerCharacteristics
from AuxStructs.InteractionsProfile import InteractionsProfile

from ModelBridge.PlayerModelBridge import PlayerModelBridge 
from ModelBridge.TaskModelBridge import TaskModelBridge 

players = numpy.empty(100)
tasks = numpy.empty(100)

class CustomTaskModelBridge(TaskModelBridge):
	
	def registerNewTask(self, taskId, description, minRequiredAbility, profile):
		pass

	def getSelectedTaskIds(self):
		pass

	def getTaskInteractionsProfile(taskId):
		pass

	def getTaskMinRequiredAbility(taskId):
		pass

	def getTaskDifficultyWeight(taskId):
		pass

	def getTaskProfileWeight(taskId):
		pass


class CustomPlayerModelBridge(PlayerModelBridge):
	
	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		players[playerId] = Player(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality)
		pass
	

	def saveplayerIncreases(self, playerId, stateIncreases):
		players[playerId].pastModelIncreasesGrid.pushToGrid(stateIncreases)

	def resetPlayer(self, playerId):
		return 0


	def getSelectedPlayerIds(self):
		playerIds = numpy.empty(100)
		for i in range(100):
			playerIds[i]=i
		return playerIds
	

	def getPlayerName(self, playerId):
		return players[playerId].name

	def getPlayerCurrProfile(self,  playerId):
		return players[playerId].currState.profile

	def getPlayerPastModelIncreases(self, playerId):
		return players[playerId].pastModelIncreasesGrid.cells

	def getPlayerCurrCharacteristics(self, playerId):
		return players[playerId].currState.characteristics
	
	def getPlayerPersonality(self, playerId):
		return players[playerId].personality


	def setPlayerCharacteristics(self, playerId, characteristics):
		players[playerId].currState.characteristics = characteristics

	def setPlayerCurrProfile(self, playerId, profile):
		players[playerId].currState.profile = profile

playerBridge = CustomPlayerModelBridge()
for x in range(100):
	playerBridge.registerNewPlayer(x, "name", PlayerState(), PlayerStateGrid(numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell), PlayerCharacteristics(), None)

taskBridge = CustomTaskModelBridge()
for x in range(100):
	taskBridge.registerNewTask(x, "description", 100, InteractionsProfile(0.1,0.3,0.8))

adaptation = Adaptation()
adaptation.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), playerBridge, taskBridge, name="", numberOfConfigChoices=50, maxNumberOfPlayersPerGroup = 3, difficultyWeight = 0.5, profileWeight=0.5)
adaptation.iterate()
adaptation.iterate()
adaptation.iterate()