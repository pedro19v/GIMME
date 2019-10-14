from abc import ABC, abstractmethod
from Player.PlayerStructs import *

class PlayerModelBridge(ABC):

	# public:
	@abstractmethod
	def saveplayerIncreases(self, playerId, stateIncreases):
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
	def getPlayerCurrProfile(self,  playerId):
		pass

	@abstractmethod
	def getPlayerPastModelIncreases(self, playerId):
		pass

	@abstractmethod
	def getPlayerCurrState(self, playerId):
		pass
		
	@abstractmethod
	def getPlayerPersonality(self, playerId):
		pass


	@abstractmethod
	def setPlayerCharacteristics(self, playerId, characteristics):
		pass

	@abstractmethod
	def setPlayerCurrProfile(self, playerId, profile):
		pass

