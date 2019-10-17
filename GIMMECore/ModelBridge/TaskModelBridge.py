from abc import ABC, abstractmethod
from PlayerStructs import *

class TaskModelBridge(ABC):

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