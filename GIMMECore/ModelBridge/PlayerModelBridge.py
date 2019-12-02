from abc import ABC, abstractmethod
from PlayerStructs import *

class PlayerModelBridge(ABC):

	@abstractmethod
	def savePlayerState(self, playerId, newState):
		pass

	@abstractmethod
	def setPlayerCharacteristics(self, playerId, characteristics):
		pass

	@abstractmethod
	def resetPlayer(self, playerId):
		pass


	@abstractmethod
	def getAllPlayerIds(self):
		pass

	@abstractmethod
	def getPlayerName(self, playerId):
		pass


	@abstractmethod
	def getPlayerCurrState(self,  playerId):
		pass

	@abstractmethod
	def getPlayerCurrCharacteristics(self, playerId):
		pass
		

	@abstractmethod
	def getPlayerStateGrid(self, playerId):
		pass

	@abstractmethod
	def getPlayerPersonality(self, playerId):
		pass
		