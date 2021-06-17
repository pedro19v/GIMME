from GIMMECore import TaskModelBridge
from GIMMECore import PlayerModelBridge

class PlayerModelMock(object):
	def __init__(self, id, name, currState, pastModelIncreasesGrid, currModelIncreases, personalityEst, realPersonality):
		self.currState = currState
		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = pastModelIncreasesGrid

		self.personalityEst = personalityEst.normalized()
		self.realPersonality = realPersonality.normalized()
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
		self.numTasks = len(tasks)

	def registerNewTask(self, taskId, description, minRequiredAbility, profile, minDuration, difficultyWeight, profileWeight):
		self.tasks[taskId] = TaskModelMock(taskId, description, minRequiredAbility, profile, minDuration, difficultyWeight, profileWeight)
	def getAllTaskIds(self):
		return [int(i) for i in range(self.numTasks)]
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
	def getTaskInitDate(self, taskId):
		return self.tasks[taskId].initDate
	def getTaskFinalDate(self, taskId):
		return self.tasks[taskId].finalDate


class CustomPlayerModelBridge(PlayerModelBridge):
	def __init__(self, players):
		self.players = players
		self.numPlayers = len(players)


	def registerNewPlayer(self, playerId, name, currState, pastModelIncreasesGrid, currModelIncreases, personalityEst, realPersonality):
		self.players[int(playerId)] = PlayerModelMock(playerId, name, currState, pastModelIncreasesGrid, currModelIncreases,  personalityEst, realPersonality)	
	def resetPlayer(self, playerId):
		self.players[int(playerId)].currState.reset()
		self.players[int(playerId)].pastModelIncreasesGrid.reset()
	def resetState(self, playerId):
		self.players[int(playerId)].currState.reset()
	def setAndSavePlayerStateToGrid(self, playerId, increases, newState):
		self.players[int(playerId)].currState = newState
		self.players[int(playerId)].pastModelIncreasesGrid.pushToDataFrame(increases)

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
	def getPlayerStatesDataFrame(self, playerId):
		return self.players[int(playerId)].pastModelIncreasesGrid
	def getPlayerCurrCharacteristics(self, playerId):
		return self.players[int(playerId)].currState.characteristics
	def getPlayerPersonalityEst(self, playerId):
		return self.players[int(playerId)].personalityEst

	def setPlayerPersonalityEst(self, playerId, personalityEst):
		self.players[int(playerId)].personalityEst = personalityEst

	def setPlayerCharacteristics(self, playerId, characteristics):
		self.players[int(playerId)].currState.characteristics = characteristics
	def setPlayerProfile(self, playerId, profile):
		self.players[int(playerId)].currState.profile = profile

	def setPlayerGroup(self, playerId, group):
		self.players[int(playerId)].currState.group = group

	def setPlayerTasks(self, playerId, tasks):
		self.players[int(playerId)].currState.tasks = tasks

	def setPlayerRealPersonality(self, playerId, realPersonality):
		self.players[int(playerId)].realPersonality = realPersonality
	def getPlayerRealPersonality(self, playerId):
		return self.players[int(playerId)].realPersonality