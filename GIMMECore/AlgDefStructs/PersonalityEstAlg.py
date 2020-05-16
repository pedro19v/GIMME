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
	def __init__(self, playerModelBridge, interactionsProfileTemplate, regAlg, numTestedPlayerProfiles = 100, qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5)):
		super().__init__(playerModelBridge)
		self.playerModelBridge = playerModelBridge
		self.qualityWeights = qualityWeights

		self.numTestedPlayerProfiles = numTestedPlayerProfiles
		self.interactionsProfileTemplate = interactionsProfileTemplate

		self.regAlg = regAlg

	def calcQuality(self, state):
		return self.qualityWeights.ability*state.characteristics.ability + self.qualityWeights.engagement*state.characteristics.engagement
	
	def updateEstimates(self):
		playerIds = self.playerModelBridge.getAllPlayerIds()
		for playerId in playerIds:
			currPersonalityEst = self.playerModelBridge.getPlayerPersonalityEst(playerId)
			newPersonalityEst = currPersonalityEst
			if(currPersonalityEst != None):
				bestQuality = self.calcQuality(self.regAlg.predict(currPersonalityEst, playerId))
			else:
				bestQuality = -1
			for i in range(self.numTestedPlayerProfiles):
				profile = self.interactionsProfileTemplate.generateCopy().randomized()
				currQuality = self.calcQuality(self.regAlg.predict(profile, playerId))
				if currQuality >= bestQuality:
					bestQuality = currQuality
					newPersonalityEst = profile

			self.playerModelBridge.setPlayerPersonalityEst(playerId, newPersonalityEst)