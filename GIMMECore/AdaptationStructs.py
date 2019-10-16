import numpy
from AuxStructs.InteractionsProfile import InteractionsProfile
from PlayerStructs import *

# auxiliary structures: Adaptation

class AdaptationGroup(object):
	def __init__(self, interactionsProfile = InteractionsProfile()):
		self.interactionsProfile = interactionsProfile

		self.avgPersonality = InteractionsProfile()
		self.avgPlayerState = PlayerState()

		self.tailoredTaskId = -1

		self.playerIds = []

	def addPlayer(self, playerModelBridge, playerId):
		self.playerIds=numpy.append(self.playerIds, playerId);
		playersSize = len(self.playerIds);

		# recalculate averages
		self.avgPlayerState = PlayerState();

		for i in range(playersSize):
			currPlayerId = self.playerIds[i];

			currPlayerState = playerModelBridge.getPlayerCurrState(currPlayerId)
			self.avgPlayerState.characteristics.engagement += currPlayerState.characteristics.engagement / playersSize;
			self.avgPlayerState.characteristics.ability += currPlayerState.characteristics.ability / playersSize;
			
			currPlayerPersonality = playerModelBridge.getPlayerPersonality(currPlayerId);
			self.avgPersonality.K_i  += currPlayerPersonality.K_i / playersSize;
			self.avgPersonality.K_cp  += currPlayerPersonality.K_cp / playersSize;
			self.avgPersonality.K_cl  += currPlayerPersonality.K_cl / playersSize;
		
		

class AdaptationConfiguration(object):	
	def __init__(self, groups=numpy.empty(0)):
		self.groups = groups