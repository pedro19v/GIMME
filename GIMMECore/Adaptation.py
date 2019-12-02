import math
from AlgDefStructs.RegressionAlg import *
from AlgDefStructs.ConfigsGenAlg import *
from AlgDefStructs.FitnessAlg import *

from ModelBridge.PlayerModelBridge import PlayerModelBridge 
from ModelBridge.TaskModelBridge import TaskModelBridge 

class Adaptation(object):

	def init(self, \
		playerModelBridge, \
		taskModelBridge, \
		configsGenAlg = None, \
		name=""):

		self.initialized = True
		self.playerIds = []
		self.taskIds = []
		self.name = name

		# self.numTasksPerGroup = numTasksPerGroup;
		self.configsGenAlg = configsGenAlg
		self.playerModelBridge = playerModelBridge
		self.taskModelBridge = taskModelBridge

	def getName(self):
		return self.name;

	def iterate(self):
		if not self.initialized:
			raise ValueError('Adaptation not Initialized! Core not executed.') 
			return

		self.playerIds = self.playerModelBridge.getAllPlayerIds()
		self.taskIds = self.taskModelBridge.getAllTaskIds()

		adaptedConfig = self.configsGenAlg.organize()

		adaptedGroups = adaptedConfig["groups"]
		adaptedProfiles = adaptedConfig["profiles"]
		adaptedAvgStates = adaptedConfig["avgStates"]

		for groupIndex in range(len(adaptedGroups)):
			currGroup = adaptedGroups[groupIndex]
			groupProfile = adaptedProfiles[groupIndex]
			avgState = adaptedAvgStates[groupIndex]
			
			tailoredTaskId = self.selectTask(self.taskIds, groupProfile, avgState)

			for playerId in currGroup:
				currState = self.playerModelBridge.getPlayerCurrState(playerId)
				currState.profile = groupProfile	
				currState.tailoredTaskId = tailoredTaskId	
				self.playerModelBridge.updatePlayerState(playerId, currState)

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
			cost += abs(avgState.characteristics.ability - self.taskModelBridge.getMinTaskRequiredAbility(currTaskId) * self.taskModelBridge.getTaskProfileWeight(currTaskId))

			if cost < lowestCost:
				lowestCost = cost
				bestTaskId = currTaskId
				
		return bestTaskId
