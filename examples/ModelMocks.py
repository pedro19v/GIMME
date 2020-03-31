from GIMMECore import TaskModelBridge
from GIMMECore import PlayerModelBridge

class PlayerModelMock(object):
	def __init__(self, id, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		self.currState = currState
		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = pastModelIncreasesGrid
		self.personality = personality
		self.baseLearningRate = None

class TaskModelMock(object):
	def __init__(self, id, description, minRequiredAbility, profile, minDuration, difficultyWeight, profileWeight):
		self.id = id
		self.description = description
		self.minRequiredAbility = minRequiredAbility
		self.profile = profile
		self.difficultyWeight = difficultyWeight
		self.profileWeight = profileWeight
		self.minDuration = minDuration

class CustomTaskModelBridge(TaskModelBridge):
	def __init__(self, tasks):
		self.tasks = tasks

	def registerNewTask(self, taskId, description, minRequiredAbility, profile, minDuration, difficultyWeight, profileWeight):
		self.tasks[taskId] = TaskModelMock(taskId, description, minRequiredAbility, profile, minDuration, difficultyWeight, profileWeight)
	def getAllTaskIds(self):
		return [int(i) for i in range(20)]
	def getTaskInteractionsProfile(self, taskId):
		return self.tasks[taskId].profile
	def getMinTaskRequiredAbility(self, taskId):
		return self.tasks[taskId].minRequiredAbility
	def getMinTaskDuration(self, taskId):
		return self.tasks[taskId].minDuration
	def getTaskDifficultyWeight(self, taskId):
		return self.tasks[taskId].difficultyWeight
	def getTaskProfileWeight(self, taskId):
		return self.tasks[taskId].profileWeight


class CustomPlayerModelBridge(PlayerModelBridge):
	def __init__(self, players):
		self.players = players
		self.numPlayers = len(players)


	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		self.players[int(playerId)] = PlayerModelMock(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personality)	
	def resetPlayer(self, playerId):
		self.players[int(playerId)].currState.reset()
	def updatePlayerState(self, playerId, newState):
		self.players[int(playerId)].currState = newState
	def savePlayerState(self, playerId, increases, newState):
		self.players[int(playerId)].currState = newState
		self.players[int(playerId)].pastModelIncreasesGrid.pushToGrid(increases)

	def setBaseLearningRate(self, playerId, blr):
		self.players[int(playerId)].baseLearningRate = blr
	def getBaseLearningRate(self, playerId):
		return self.players[int(playerId)].baseLearningRate

	def getAllPlayerIds(self):
		return [int(i) for i in range(self.numPlayers)]

	def getPlayerName(self, playerId):
		return self.players[int(playerId)].name
	def getPlayerCurrState(self,  playerId):
		return self.players[int(playerId)].currState
	def getPlayerCurrProfile(self,  playerId):
		return self.players[int(playerId)].currState.profile
	def getPlayerStateGrid(self, playerId):
		return self.players[int(playerId)].pastModelIncreasesGrid
	def getPlayerCurrCharacteristics(self, playerId):
		return self.players[int(playerId)].currState.characteristics
	def getPlayerPersonality(self, playerId):
		return self.players[int(playerId)].personality

	def setPlayerPersonality(self, playerId, personality):
		self.players[int(playerId)].personality = personality
	def setPlayerCharacteristics(self, playerId, characteristics):
		self.players[int(playerId)].currState.characteristics = characteristics
