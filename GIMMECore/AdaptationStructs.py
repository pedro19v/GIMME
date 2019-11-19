import json
from AuxStructs.InteractionsProfile import InteractionsProfile
from PlayerStructs import *

# auxiliary structures: Adaptation

class AdaptationGroup(object):
	def __init__(self):
		self.profile = InteractionsProfile()

		self.avgPersonality = InteractionsProfile()
		self.avgPlayerState = PlayerState()

		self.tailoredTaskId = -1

		self.playerIds = []

		self.fitness = 0

	def addPlayer(self, playerModelBridge, playerId):
		self.playerIds.append(playerId);
		playersSize = len(self.playerIds);

		# recalculate averages
		self.avgPersonality.reset()
		self.avgPlayerState.reset()

		for i in range(playersSize):
			playersSize = float(playersSize)
			currPlayerId = self.playerIds[i];

			currPlayerCharacteristics = playerModelBridge.getPlayerCurrCharacteristics(currPlayerId)
			self.avgPlayerState.characteristics.engagement += currPlayerCharacteristics.engagement / playersSize;
			self.avgPlayerState.characteristics.ability += currPlayerCharacteristics.ability / playersSize;
			
			currPlayerPersonality = playerModelBridge.getPlayerPersonality(currPlayerId)
			# print(currPlayerPersonality.K_i)
			# print(currPlayerPersonality.K_cp)
			# print(currPlayerPersonality.K_cl)
			self.avgPersonality.K_i  += currPlayerPersonality.K_i / playersSize;
			self.avgPersonality.K_cp  += currPlayerPersonality.K_cp / playersSize;
			self.avgPersonality.K_mh  += currPlayerPersonality.K_mh / playersSize;
			self.avgPersonality.K_pa  += currPlayerPersonality.K_pa / playersSize;
		
		

class AdaptationConfiguration(object):	
	def __init__(self):
		self.groups = []