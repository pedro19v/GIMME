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
		configsGenAlg = None):

		self.initialized = True
		self.playerIds = []
		self.taskIds = []
		self.name = name

		# self.numTasksPerGroup = numTasksPerGroup;
		self.configsGenAlg = configsGenAlg
		self.playerModelBridge = playerModelBridge
		self.taskModelBridge = taskModelBridge

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
		adaptedConfig["adaptedTaskId"] = -1

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
				currState.adaptedTaskId = adaptedTaskId	
				self.playerModelBridge.setPlayerCharacteristics(playerId, currState.characteristics)
				self.playerModelBridge.setPlayerProfile(playerId, currState.profile)

				groupStr += str(self.playerModelBridge.getPlayerPersonalityEst(playerId).dimensions.values())+",\n"

			adaptedConfig["adaptedTaskId"] = adaptedTaskId


			groupStr += ",groupPrf: "+ str(groupProfile.dimensions.values()) +" ],\n\n"

		groupStr += "]"
		# print(groupStr)
		# breakpoint()

		return adaptedConfig

	def selectTask(self,
		possibleTaskIds,
		bestConfigProfile,
		avgState):
		lowestCost = math.inf
		bestTaskId = -1 #if no tasks are available 

		for i in range(len(possibleTaskIds)):
			currTaskId = possibleTaskIds[i]

			cost = abs(bestConfigProfile.sqrDistanceBetween(self.taskModelBridge.getTaskInteractionsProfile(currTaskId)) * self.taskModelBridge.getTaskDifficultyWeight(currTaskId))
			cost += abs(avgState.ability - self.taskModelBridge.getMinTaskRequiredAbility(currTaskId) * self.taskModelBridge.getTaskProfileWeight(currTaskId))

			if cost < lowestCost:
				lowestCost = cost
				bestTaskId = currTaskId
				
		return bestTaskId
