import math
from AlgDefStructs.RegressionAlg import *
from AlgDefStructs.ConfigsGenAlg import *
from AlgDefStructs.FitnessAlg import *
from AdaptationStructs import *

from ModelBridge.PlayerModelBridge import PlayerModelBridge 
from ModelBridge.TaskModelBridge import TaskModelBridge 

class Adaptation(object):

	def init(self, \
		playerModelBridge, \
		taskModelBridge, \
		regAlg = None, \
		configsGenAlg = None, \
		fitAlg = None, \
		name="", \
		numberOfConfigChoices=100, \
		preferredNumberOfPlayersPerGroup = None,\
		minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5):

		if(minNumberOfPlayersPerGroup > maxNumberOfPlayersPerGroup):
			raise ValueError('The min number of players per group cannot be higher than the max!') 

		self.initialized = True

		self.playerIds = []
		self.taskIds = []

		self.name = name

		self.numberOfConfigChoices = numberOfConfigChoices
		if preferredNumberOfPlayersPerGroup == None:
			self.maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup
			self.minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup
		else:
			self.maxNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup
			self.minNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup

		# self.numTasksPerGroup = numTasksPerGroup;
		self.regAlg = regAlg
		self.fitAlg = fitAlg
		self.configsGenAlg = configsGenAlg

		self.playerModelBridge = playerModelBridge
		self.taskModelBridge = taskModelBridge

	def getName(self):
		return self.name;

	def iterate(self):
		if not self.initialized:
			raise ValueError('Adaptation not Initialized! Core not executed.') 
			return


		self.playerIds = self.playerModelBridge.getSelectedPlayerIds()
		self.taskIds = self.taskModelBridge.getSelectedTaskIds()

		adaptedConfig = self.organizePlayers(self.playerIds)
		groups = adaptedConfig.groups
		groupsSize = len(groups)
		for i in range(groupsSize):
			currGroup = groups[i];
			groupPlayers = currGroup.playerIds
			groupPlayersSize = len(groupPlayers)

			for j in range(groupPlayersSize):
				currPlayer = groupPlayers[j]
				self.playerModelBridge.setPlayerCurrProfile(currPlayer, currGroup.profile);

			currGroupProfile = currGroup.profile
			currGroupState = currGroup.avgPlayerState
			currGroup.tailoredTaskId = self.selectTask(self.taskIds, currGroupProfile, currGroupState)

		return adaptedConfig


	def organizePlayers(self, playerIds):
		return self.configsGenAlg.organize(self.playerModelBridge, playerIds, self.numberOfConfigChoices, self.minNumberOfPlayersPerGroup, self.maxNumberOfPlayersPerGroup, self.regAlg, self.fitAlg);

	def selectTask(self,
		possibleTaskIds,
		bestConfigProfile,
		avgLearningState):
		lowestCost = math.inf
		bestTaskId = -1 #if no tasks are available 

		for i in range(len(possibleTaskIds)):
			currTaskId = possibleTaskIds[i]

			cost = abs(bestConfigProfile.sqrDistanceBetween(self.taskModelBridge.getTaskInteractionsProfile(currTaskId)) * self.taskModelBridge.getTaskDifficultyWeight(currTaskId))
			cost += abs(avgLearningState.characteristics.ability - self.taskModelBridge.getTaskMinRequiredAbility(currTaskId) * self.taskModelBridge.getTaskProfileWeight(currTaskId))

			if cost < lowestCost:
				lowestCost = cost
				bestTaskId = currTaskId
				
		return bestTaskId
