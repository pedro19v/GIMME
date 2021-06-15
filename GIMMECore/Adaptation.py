import math
from .AlgDefStructs.RegressionAlg import *
from .AlgDefStructs.ConfigsGenAlg import *
from .AlgDefStructs.PersonalityEstAlg import *

from .ModelBridge.PlayerModelBridge import PlayerModelBridge 
from .ModelBridge.TaskModelBridge import TaskModelBridge 


class Adaptation(object):

	def init(self, \
		playerModelBridge, \
		taskModelBridge, \
		name, \
		configsGenAlg):

		self.initialized = True
		self.playerIds = []
		self.taskIds = []
		self.name = name

		# self.numTasksPerGroup = numTasksPerGroup;
		self.configsGenAlg = configsGenAlg
		self.playerModelBridge = playerModelBridge
		self.taskModelBridge = taskModelBridge

		self.configsGenAlg.init()	


	def iterate(self):
		if not self.initialized:
			raise AssertionError('Adaptation not Initialized! Core not executed.') 
			return
		
		self.playerIds = self.playerModelBridge.getAllPlayerIds()
		self.taskIds = self.taskModelBridge.getAllTaskIds()

		if len(self.playerIds) < self.configsGenAlg.minNumberOfPlayersPerGroup:
			raise ValueError('Not enough players to form a group.') 
			return
		

		adaptedConfig = self.configsGenAlg.organize()

		adaptedGroups = adaptedConfig["groups"]
		adaptedProfiles = adaptedConfig["profiles"]
		adaptedAvgCharacteristics = adaptedConfig["avgCharacteristics"]
		adaptedConfig["tasks"] = []

		groupStr = "["

		for groupIndex in range(len(adaptedGroups)):
			currGroup = adaptedGroups[groupIndex]
			groupProfile = adaptedProfiles[groupIndex]
			avgState = adaptedAvgCharacteristics[groupIndex]
		
			groupStr += "["

			adaptedTaskId = self.selectTask(self.taskIds, groupProfile, avgState)
			for playerId in currGroup:

				currState = self.playerModelBridge.getPlayerCurrState(playerId)
				currState.profile = groupProfile	
				self.playerModelBridge.setPlayerTasks(playerId, [adaptedTaskId])
				self.playerModelBridge.setPlayerCharacteristics(playerId, currState.characteristics)
				self.playerModelBridge.setPlayerProfile(playerId, currState.profile)
				self.playerModelBridge.setPlayerGroup(playerId, currGroup)

				groupStr += str(self.playerModelBridge.getPlayerPersonalityEst(playerId).dimensions.values())+",\n"

			adaptedConfig["tasks"].append(adaptedTaskId)

			groupStr += ",groupPrf: "+ str(groupProfile.dimensions.values()) +" ],\n\n"
			
		groupStr += "]"

		return adaptedConfig

	def selectTask(self,
		possibleTaskIds,
		bestConfigProfile,
		avgState):
		lowestCost = math.inf
		bestTaskId = -1 #if no tasks are available 

		for i in range(len(possibleTaskIds)):
			currTaskId = possibleTaskIds[i]

			cost = abs(bestConfigProfile.sqrDistanceBetween(self.taskModelBridge.getTaskInteractionsProfile(currTaskId)) * self.taskModelBridge.getTaskProfileWeight(currTaskId))
			cost += abs(avgState.ability - self.taskModelBridge.getMinTaskRequiredAbility(currTaskId) * self.taskModelBridge.getTaskDifficultyWeight(currTaskId))

			if cost < lowestCost:
				lowestCost = cost
				bestTaskId = currTaskId
				
		return bestTaskId





	# Bootstrap
	def simulateReaction(self, playerId):
		currState = self.playerModelBridge.getPlayerCurrState(playerId)
		newState = self.calcReaction(state = currState, playerId = playerId)

		increases = PlayerState(stateType = newState.stateType)
		increases.profile = currState.profile
		increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
		self.playerModelBridge.setAndSavePlayerStateToGrid(playerId, increases, newState)	
		return increases

	def calcReaction(self, state, playerId):
		personality = self.playerModelBridge.getPlayerRealPersonality(playerId)
		numDims = len(personality.dimensions)
		newState = PlayerState(
			stateType = 0, 
			characteristics = PlayerCharacteristics(
				ability=state.characteristics.ability, 
				engagement=state.characteristics.engagement
				), 
			profile=state.profile)
		newState.characteristics.engagement = 1 - (personality.distanceBetween(state.profile) / math.sqrt(numDims))  #between 0 and 1
		if newState.characteristics.engagement>1:
			raise ValueError('Something went wrong. Engagement is > 1.') 
		abilityIncreaseSim = (newState.characteristics.engagement*self.playerModelBridge.getBaseLearningRate(playerId))
		newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
		return newState

	def bootstrap(self, numBootstrapIterations):
		if(numBootstrapIterations <= 0):
			raise ValueError('Number of bootstrap iterations must be higher than 0 for this method to be called.') 
			return

		numPlayers = len(self.playerModelBridge.getAllPlayerIds())
		i = 0
		while(i < numBootstrapIterations):
			print("Performming step ("+str(i)+" of "+str(numBootstrapIterations)+") of the bootstrap phase of \""+str(self.name)+"\"...                                                             ", end="\r")
			self.iterate()
			for x in range(numPlayers):
				increases = self.simulateReaction(playerId=x)	
			i+=1


		self.configsGenAlg.reset()
