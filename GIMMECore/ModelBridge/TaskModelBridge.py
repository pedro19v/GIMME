from abc import ABC, abstractmethod
from PlayerStructs import *

class TaskModelBridge(ABC):

	@abstractmethod
	def getAllTaskIds(self):
		pass

	@abstractmethod
	def getTaskInteractionsProfile(self, taskId):
		pass

	@abstractmethod
	def getTaskMinRequiredAbility(self, taskId):
		pass

	@abstractmethod
	def getTaskMinDuration(self, taskId):
		pass

	@abstractmethod
	def getTaskDifficultyWeight(self, taskId):
		pass

	@abstractmethod
	def getTaskProfileWeight(self, taskId):
		pass