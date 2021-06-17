import math
import time
import copy
import json
from .InteractionsProfile import InteractionsProfile



class PlayerCharacteristics(object):
	def __init__(self, ability = None, engagement = None):
		self.ability = 0 if ability==None else ability
		self.engagement = 0 if engagement==None else engagement
	def reset(self):
		self.ability = 0
		self.engagement = 0
		return self

class PlayerState(object):
	def __init__(self, stateType = None, profile = None, characteristics = None, dist = None, quality = None, group = None, tasks = None):
		self.creationTime = time.time()
		
		self.stateType = 1 if stateType == None else stateType
		self.profile = InteractionsProfile() if profile == None else profile
		self.characteristics = PlayerCharacteristics() if characteristics == None else characteristics
		self.dist = -1 if dist == None else dist
		self.quality = -1 if quality == None else quality

		self.group = [] if group == None else group
		self.tasks = [] if tasks == None else tasks


	def reset(self):
		self.characteristics.reset()
		self.profile.reset()
		self.creationTime = time.time()
		self.stateType = 1
		self.quality = -1
		self.dist = -1
		
		self.group = []
		self.tasks = []
		return self


class PlayerStateDataFrame(object):
	def __init__(self, interactionsProfileTemplate, gridTrimAlg, states = None):
		self.interactionsProfileTemplate = interactionsProfileTemplate
		self.gridTrimAlg = gridTrimAlg

		self.states = [] if states == None else states

		#auxiliary stuff
		self.flatProfiles = []
		self.flatAbilities = []
		self.flatEngagements = []

	def reset(self):
		self.states = [] if states == None else states
		
		#auxiliary stuff
		self.flatProfiles = []
		self.flatAbilities = []
		self.flatEngagements = []

		return self

	def pushToDataFrame(self, playerState):
		self.states.append(playerState)
		flatProfiles.append([dim for dim in playerState.profile.dimensions])
		flatAbilities.append(playerState.profile.characteristics.ability)
		flatEngagements.append(playerState.profile.characteristics.engagement)

		trimmedList = self.gridTrimAlg.trimmedList(self.states)

		self.state = trimmedList[0] 
		for state in self.trimmedList[1]:
			flatProfiles.remove([dim for dim in state.profile.dimensions])
			flatAbilities.remove(state.profile.characteristics.ability)
			flatEngagements.remove(state.profile.characteristics.ability)


	def getAllStates(self):
		return self.states


	def getAllStatesFlatten(self):
		return {'profiles': self.flatProfiles, 'abilities': self.flatAbilities, 'engagements': self.flatEngagements}

	def getNumStates(self):
		return len(self.states)
