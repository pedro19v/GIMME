import math
from AlgDefStructs.RegressionAlg import *
from AlgDefStructs.ConfigsGenAlg import *
from AlgDefStructs.FitnessAlg import *
from AdaptationStructs import *

from ModelBridge.PlayerModelBridge import PlayerModelBridge 
from ModelBridge.TaskModelBridge import TaskModelBridge 

class Adaptation(object):

	def init(self, \
		regAlg, \
		configsGenAlg, \
		fitAlg, \
		playerModelBridge, \
		taskModelBridge, \
		name="", \
		numberOfConfigChoices=100, \
		minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5, \
		randomGen = RandomGen(), \
		difficultyWeight = 0.5, \
		profileWeight=0.5):
		
		self.playerIds = []
		self.taskIds = []

		self.name = name

		self.numberOfConfigChoices = numberOfConfigChoices
		self.maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup
		self.minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup

		# self.numTasksPerGroup = numTasksPerGroup;
		self.regAlg = regAlg
		self.fitAlg = fitAlg
		self.configsGenAlg = configsGenAlg

		self.randomGen = randomGen

		self.difficultyWeight = difficultyWeight
		self.profileWeight = profileWeight

		self.playerModelBridge = playerModelBridge
		self.taskModelBridge = taskModelBridge

	def getName(self):
		return self.name;

	def iterate(self):
		self.playerIds = self.playerModelBridge.getSelectedPlayerIds()
		self.taskIds = self.taskModelBridge.getSelectedTaskIds()
		# self.tasks = taskModelBridge.getAllTaskIds()
		adaptedConfig = self.organizePlayers(self.playerIds)
		groups = adaptedConfig.groups
		groupsSize = len(groups)
		for i in range(groupsSize):
			currGroup = groups[i];
			groupPlayers = currGroup.playerIds
			groupPlayersSize = len(groupPlayers)

			for j in range(groupPlayersSize):
				currPlayer = groupPlayers[j]
				self.playerModelBridge.setPlayerCurrProfile(currPlayer, currGroup.interactionsProfile);

			currGroupProfile = currGroup.interactionsProfile
			currGroupState = currGroup.avgPlayerState
			currGroup.tailoredTask = self.selectTask(self.taskIds, currGroupProfile, currGroupState)
		return adaptedConfig


	def organizePlayers(self, playerIds):
		return self.configsGenAlg.organize(self.playerModelBridge, playerIds, self.numberOfConfigChoices, self.minNumberOfPlayersPerGroup, self.maxNumberOfPlayersPerGroup, self.randomGen, self.regAlg, self.fitAlg);

	def selectTask(self,
		possibleTaskIds,
		bestConfigProfile,
		avgLearningState):
		lowestCost = math.inf
		bestTask = None
		for i in range(len(possibleTaskIds)):
			currTask = possibleTaskIds[i]
			cost = abs(bestConfigProfile.distanceBetween(self.taskModelBridge.getTaskInteractionsProfile(currTask)) * self.taskModelBridge.getTaskDifficultyWeight(currTask))
			cost += abs(avgLearningState.characteristics.ability - self.taskModelBridge.getTaskMinRequiredAbility(currTask) * self.taskModelBridge.getTaskProfileWeight(currTask))

			if cost < lowestCost:
				lowestCost = cost
				bestTask = currTask
		return bestTask
