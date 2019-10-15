from abc import ABC, abstractmethod
from Player.PlayerStructs import *

class TaskModelBridge(ABC):

	@abstractmethod
	def registerNewTask(self, taskId, description, minRequiredAbility, profile, tasks):
		pass

	@abstractmethod
	def getSelectedTaskIds(self):
		pass

	@abstractmethod
	def getTaskInteractionsProfile(self, taskId):
		pass

	@abstractmethod
	def getTaskMinRequiredAbility(self, taskId):
		pass

	@abstractmethod
	def getTaskDifficultyWeight(self, taskId):
		pass

	@abstractmethod
	def getTaskProfileWeight(self, taskId):
		pass