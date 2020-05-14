from abc import ABC, abstractmethod
from ..PlayerStructs import *
import json

class PersonalityEstAlg(ABC):

	def __init__(self, playerModelBridge):
		self.playerModelBridge = playerModelBridge

	@abstractmethod
	def updateEstimates(self):
		pass


class SimplePersonalityEstAlg(PersonalityEstAlg):
	def __init__(self, playerModelBridge, qualityFunc):
		super().__init__(playerModelBridge)
		self.playerModelBridge = playerModelBridge
		self.qualityFunc = qualityFunc

		self.bestQualities = {}

	def updateEstimates(self):
		playerIds = self.playerModelBridge.getAllPlayerIds()
		for player in playerIds:
			currPersonalityEst = self.playerModelBridge.getPlayerPersonalityEst(player)
			currPersonalityQuality = self.bestQualities[playerId]
			lastDataPoint = self.playerModelBridge.getPlayerCurrState(player)
			quality = self.qualityFunc(lastDataPoint)
			if quality > currPersonalityQuality:
				self.bestQualities[playerId] = currPersonalityQuality
				self.playerModelBridge.setPersonalityEst(player, lastDataPoint.profile)