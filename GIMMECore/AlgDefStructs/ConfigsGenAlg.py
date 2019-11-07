import random
import math
from abc import ABC, abstractmethod
from AdaptationStructs import *
from AuxStructs.InteractionsProfile import InteractionsProfile 

class ConfigsGenAlg(ABC):

	def __init__(self):
		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}

		super().__init__()

	@abstractmethod
	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		pass

	def updateMetrics(self, generatedConfig):
		if(self.configSizeFreqs.get(len(generatedConfig.groups))):
			self.configSizeFreqs[len(generatedConfig.groups)]+=1
		else:
			self.configSizeFreqs[len(generatedConfig.groups)]=1

		for group in generatedConfig.groups:
			if(self.configSizeFreqs.get(len(group.playerIds))):
				self.configSizeFreqs[len(group.playerIds)]+=1
			else:
				self.configSizeFreqs[len(group.playerIds)]=1



class RandomConfigsGen(ConfigsGenAlg):

	def randomProfileGenerator(self, group):
		# generate learning profile
		profile = InteractionsProfile()
		profile.K_cp = random.uniform(0, 1)
		profile.K_i = random.uniform(0, 1)
		profile.K_mh = random.uniform(0, 1)
		profile.K_pa = random.uniform(0, 1)

		# total = profile.K_cp +profile.K_i +profile.K_mh +profile.K_pa 

		# profile.K_cp /= total
		# profile.K_i /= total
		# profile.K_mh /= total
		# profile.K_pa /= total

		return profile

	def __init__(self):
		ConfigsGenAlg.__init__(self)
		self.profileGenerator = self.randomProfileGenerator

	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		bestConfig = AdaptationConfiguration()

		if(len(playerIds) < minNumberOfPlayersPerGroup):
			return bestConfig

		currMaxFitness = -float("inf")

		minNumGroups = math.ceil(len(playerIds) / maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / minNumberOfPlayersPerGroup)
		
		# generate several random groups, calculate their fitness and select the best one
		for i in range(numberOfConfigChoices):
			currFitness = 0.0
			playersWithoutGroup = playerIds.copy()
			newConfig = AdaptationConfiguration()

			if(minNumGroups < maxNumGroups):
				numGroups = random.randint(minNumGroups, maxNumGroups)
			else: # players length is 1
				numGroups = minNumGroups

			# generate min groups
			playersWithoutGroupSize = 0
			for j in range(numGroups):
				currGroup = AdaptationGroup()

				# add min number of players to the group
				for s in range(minNumberOfPlayersPerGroup):
					playersWithoutGroupSize = len(playersWithoutGroup)
					currPlayerIndex = random.randint(0, playersWithoutGroupSize - 1)

					currPlayerID = playersWithoutGroup[currPlayerIndex]
					currGroup.addPlayer(playerModelBridge, currPlayerID)

					del playersWithoutGroup[currPlayerIndex]
				
				newConfig.groups.append(currGroup)

			# append the rest
			playersWithoutGroupSize = len(playersWithoutGroup);
			while playersWithoutGroupSize > 0:
				randomGroupIndex = random.randint(0, len(newConfig.groups) - 1)

				currPlayerIndex = 0;
				if (playersWithoutGroupSize > 1):
					currPlayerIndex = random.randint(0, playersWithoutGroupSize - 1)
				else:
					currPlayerIndex = 0

				currGroup = newConfig.groups[randomGroupIndex];
				groupsSize = len(newConfig.groups);
				while (len(currGroup.playerIds) > maxNumberOfPlayersPerGroup - 1):
					randomGroupIndex+=1
					currGroup = newConfig.groups[randomGroupIndex%groupsSize]

				currPlayer = playersWithoutGroup[currPlayerIndex];
				currGroup.addPlayer(playerModelBridge, currPlayer);

				del playersWithoutGroup[currPlayerIndex]
				playersWithoutGroupSize = len(playersWithoutGroup)

			playerSize = len(playerIds)
			currGroups = newConfig.groups
			currGroupsSize = len(currGroups)

			# generate profiles
			for group in currGroups:
				# generate learning profile
				group.profile = self.profileGenerator(group)
				for currPlayer in group.playerIds:
					currPlayerFitness = fitAlg.calculate(playerModelBridge, currPlayer, group.profile, regAlg)
					currFitness += currPlayerFitness

			# print(json.dumps(group, default=lambda o: o.__dict__, sort_keys=True))
			if (currFitness > currMaxFitness):
				bestConfig = newConfig
				currMaxFitness = currFitness
				
		# print(json.dumps(bestConfig, default=lambda o: o.__dict__, sort_keys=True))
		self.updateMetrics(bestConfig)
		return bestConfig


class PersonalityBasedConfigsGen(RandomConfigsGen):
	def personalityBasedProfileGenerator(self, group):
		# generate learning profile
		profile = InteractionsProfile()
		profile.K_cp = random.normal(group.avgPersonality.K_cp, self.variation)
		profile.K_i = random.normal(group.avgPersonality.K_i, self.variation)
		profile.K_mh = random.normal(group.avgPersonality.K_mh, self.variation)
		profile.K_pa = random.normal(group.avgPersonality.K_pa, self.variation)
		return profile

	def __init__(self, variation):
		RandomConfigsGen.__init__(self)
		self.profileGenerator = self.personalityBasedProfileGenerator
		self.variation = variation


class EvolutionaryConfigsGen(ConfigsGenAlg):
	def organize(self, players, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):

		bestConfig = AdaptationConfiguration()
		currMaxFitness = -math.inf

		# generate several random groups, calculate their fitness and select best one
		adaptG = AdaptationGroup(InteractionsProfile(0.33, 0.33, 0.33), players)
		updateMetrics(bestConfig)
		return bestConfig

