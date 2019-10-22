from AuxStructs.InteractionsProfile import InteractionsProfile
from PlayerStructs import *

# auxiliary structures: Adaptation

class AdaptationGroup(object):
	def __init__(self):
		self.interactionsProfile = InteractionsProfile()

		self.avgPersonality = InteractionsProfile()
		self.avgPlayerState = PlayerState()

		self.tailoredTaskId = -1

		self.playerIds = []

	def addPlayer(self, playerModelBridge, playerId):
		self.playerIds.append(playerId);
		playersSize = len(self.playerIds);

		# recalculate averages
		self.avgPlayerState = PlayerState();

		for i in range(playersSize):
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
			self.avgPersonality.K_cl  += currPlayerPersonality.K_cl / playersSize;
		
		

class AdaptationConfiguration(object):	
	def __init__(self):
		self.groups = []