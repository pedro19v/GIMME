import numpy
from AuxStructs.InteractionsProfile import InteractionsProfile
from Player.PlayerStructs import *

# auxiliary structures: Adaptation
class AdaptationTask(object):
	def __init__(self, description="", minRequiredAbility=0, profile=InteractionsProfile()):
		self.description = description
		self.minRequiredAbility = minRequiredAbility
		self.profile = profile

class AdaptationGroup(object):
	def __init__(self, interactionsProfile = InteractionsProfile()):
		self.interactionsProfile = interactionsProfile

		self.avgPreferences = InteractionsProfile()
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
			
			currPlayerPreference = playerModelBridge.getPlayerPersonality(currPlayerId);
			self.avgPreferences.K_i  += currPlayerPreference.K_i / playersSize;
			self.avgPreferences.K_cp  += currPlayerPreference.K_cp / playersSize;
			self.avgPreferences.K_cl  += currPlayerPreference.K_cl / playersSize;
		
		

class AdaptationConfiguration(object):	
	def __init__(self, groups=numpy.empty(0)):
		self.groups = groups