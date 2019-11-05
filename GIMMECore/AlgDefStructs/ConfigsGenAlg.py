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

	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		bestConfig = AdaptationConfiguration()


		if(len(playerIds) < minNumberOfPlayersPerGroup):
			return bestConfig

		currMaxFitness = -1.0

		minNumGroups = math.ceil(len(playerIds) / maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / minNumberOfPlayersPerGroup)
		
		# generate several random groups, calculate their fitness and select the best one
		for i in range(numberOfConfigChoices):
			lastProfile = False
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
				currGroup = AdaptationGroup();

				# generate learning profile
				newRand1 = random.uniform(0, 1)
				newRand2 = random.uniform(0, 1)
				newRand3 = random.uniform(0, 1)
				newRand4 = random.uniform(0, 1)

				newRandSum = newRand1 + newRand2 + newRand3 + newRand4

				profile = InteractionsProfile();
				if(newRandSum > 0):
					profile.K_cp = newRand1 / newRandSum;
					profile.K_i = newRand2 / newRandSum;
					profile.K_mh = newRand3 / newRandSum;
					profile.K_pa = newRand4 / newRandSum;
				currGroup.interactionsProfile = profile;


				# add min number of players to the group
				for s in range(minNumberOfPlayersPerGroup):
					playersWithoutGroupSize = len(playersWithoutGroup)

					currPlayerIndex = random.randint(0, playersWithoutGroupSize - 1)

					currPlayerID = playersWithoutGroup[currPlayerIndex]
					currGroup.addPlayer(playerModelBridge, currPlayerID)

					currPlayerFitness = fitAlg.calculate(playerModelBridge, currPlayerID, currGroup.interactionsProfile, regAlg)
					currFitness += currPlayerFitness

					del playersWithoutGroup[currPlayerIndex]
				
				newConfig.groups.append(currGroup)

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

				currPlayerFitness = fitAlg.calculate(playerModelBridge, currPlayer, currGroup.interactionsProfile, regAlg)
				currFitness += currPlayerFitness

				del playersWithoutGroup[currPlayerIndex]
				playersWithoutGroupSize = len(playersWithoutGroup)

			playerSize = len(playerIds)
			currGroups = newConfig.groups
			currGroupsSize = len(currGroups)

			if (currFitness > currMaxFitness):
				bestConfig = newConfig
				currMaxFitness = currFitness	
		
			# print("c" + str(self.configSizeFreqs))

			self.updateMetrics(bestConfig)
		return bestConfig



class EvolutionaryConfigsGen(ConfigsGenAlg):
	def organize(self, players, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):

		bestConfig = AdaptationConfiguration()
		currMaxFitness = -math.inf

		# generate several random groups, calculate their fitness and select best one
		adaptG = AdaptationGroup(InteractionsProfile(0.33, 0.33, 0.33), players)
		updateMetrics(bestConfig)
		return bestConfig

