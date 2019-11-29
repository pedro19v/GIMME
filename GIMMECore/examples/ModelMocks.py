from GIMMECore import *
from PlayerStructs import *

numPlayers = 23

players = [None for x in range(numPlayers)]
playersGrid = [None for x in range(numPlayers)]
tasks = [None for x in range(20)]

class PlayerModelMock(object):
	def __init__(self, id, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		self.currState = currState
		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = pastModelIncreasesGrid
		self.personality = personality
		self.baseLearningRate = None

class TaskModelMock(object):
	def __init__(self, id, description, minRequiredAbility, profile, difficultyWeight, profileWeight):
		self.id = id
		self.description = description
		self.minRequiredAbility = minRequiredAbility
		self.profile = profile
		self.difficultyWeight = difficultyWeight
		self.profileWeight = profileWeight

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
	def resetPlayer(self, playerId):
		players[int(playerId)].currState.reset()
		players[int(playerId)].pastModelIncreasesGrid.reset()
	def updatePlayerState(self, playerId, newState):
		players[int(playerId)].currState = newState
	def savePlayerState(self, playerId, increases, newState):
		players[int(playerId)].currState = newState
		players[int(playerId)].pastModelIncreasesGrid.pushToGrid(increases)

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


class CustomPlayerModelBridgeGrid(PlayerModelBridge):
	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		playersGrid[int(playerId)] = PlayerModelMock(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality)	
	def resetPlayer(self, playerId):
		playersGrid[int(playerId)].currState.reset()
		playersGrid[int(playerId)].pastModelIncreasesGrid.reset()
	def updatePlayerState(self, playerId, newState):
		playersGrid[int(playerId)].currState = newState
	def savePlayerState(self, playerId, increases, newState):
		playersGrid[int(playerId)].currState = newState
		playersGrid[int(playerId)].pastModelIncreasesGrid.pushToGrid(increases)
	def setBaseLearningRate(self, playerId, blr):
		playersGrid[int(playerId)].baseLearningRate = blr
	def getBaseLearningRate(self, playerId):
		return playersGrid[int(playerId)].baseLearningRate

	def getSelectedPlayerIds(self):
		return [int(i) for i in range(numPlayers)]

	def getPlayerName(self, playerId):
		return playersGrid[int(playerId)].name
	def getPlayerCurrState(self,  playerId):
		return playersGrid[int(playerId)].currState
	def getPlayerCurrProfile(self,  playerId):
		return playersGrid[int(playerId)].currState.profile
	def getPlayerPastModelIncreases(self, playerId):
		return playersGrid[int(playerId)].pastModelIncreasesGrid
	def getPlayerCurrCharacteristics(self, playerId):
		return playersGrid[int(playerId)].currState.characteristics
	def getPlayerPersonality(self, playerId):
		return playersGrid[int(playerId)].personality

	def setPlayerPersonality(self, playerId, personality):
		playersGrid[int(playerId)].personality = personality
	def setPlayerCharacteristics(self, playerId, characteristics):
		playersGrid[int(playerId)].currState.characteristics = characteristics
