import random
import math
from abc import ABC, abstractmethod
from AdaptationStructs import *
from AuxStructs.InteractionsProfile import InteractionsProfile 

class ConfigsGenAlg(ABC):

	def __init__(self):
		self.groupSizeFreqs = numpy.empty(0)
		self.configSizeFreqs = numpy.empty(0)

		super().__init__()

	@abstractmethod
	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		pass

	def updateMetrics(self, generatedConfig):
		self.configSizeFreqs[len(generatedConfig.groups)]+=1
		for group in generatedConfig.groups:
			self.groupSizeFreqs[len(group.playerIds)]+=1



class RandomConfigsGen(ConfigsGenAlg):

	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		
		self.groupSizeFreqs = numpy.empty(len(playerIds))
		self.configSizeFreqs = numpy.empty(len(playerIds))

		bestConfig = AdaptationConfiguration()
		currMaxFitness = -1.0

		# generate several random groups, calculate their fitness and select the best one
		for j in range(numberOfConfigChoices):
			lastProfile = False
			currFitness = 0.0
			playersWithoutGroup = playerIds
			newConfig = AdaptationConfiguration()

			minNumGroups = math.ceil(len(playerIds) / maxNumberOfPlayersPerGroup);
			maxNumGroups = math.floor(len(playerIds) / minNumberOfPlayersPerGroup);
			numGroups = random.randint(minNumGroups, maxNumGroups);

			# generate min groups
			playersWithoutGroupSize = 0
			for j in range(numGroups):
				currGroup = AdaptationGroup();

				# generate learning profile
				newRand1 = random.uniform(0, 1)
				newRand2 = random.uniform(0, 1)
				newRand3 = random.uniform(0, 1)

				newRandSum = newRand1 + newRand2 + newRand3;

				profile = InteractionsProfile();
				if(newRandSum > 0):
					profile.K_cl = newRand1 / newRandSum;
					profile.K_cp = newRand2 / newRandSum;
					profile.K_i = newRand3 / newRandSum;
				currGroup.interactionsProfile = profile;


				for s in range(minNumberOfPlayersPerGroup):
					playersWithoutGroupSize = len(playersWithoutGroup)
					currPlayerIndex = random.randint(0, playersWithoutGroupSize - 1)

					currPlayerID = playersWithoutGroup[currPlayerIndex]
					currGroup.addPlayer(playerModelBridge, currPlayerID)

					currPlayerFitness = fitAlg.calculate(playerModelBridge, currPlayerID, currGroup.interactionsProfile, regAlg)
					currFitness += currPlayerFitness

					playersWithoutGroup = numpy.delete(playersWithoutGroup, currPlayerIndex)
				
				newConfig.groups = numpy.append(newConfig.groups, currGroup)

			playersWithoutGroupSize = len(playersWithoutGroup);
			
			while playersWithoutGroupSize > 0:
				randomGroupIndex = random.randint(0, len(newConfig.groups) - 1)

				currPlayerIndex = 0;
				if (playersWithoutGroupSize > 1):
					currPlayerIndex = random.randint(0, playersWithoutGroupSize - 1)

				currGroup = newConfig.groups[randomGroupIndex];
				groupsSize = len(newConfig.groups);
				while (len(currGroup.playerIds) > maxNumberOfPlayersPerGroup - 1):
					randomGroupIndex+=1
					currGroup = newConfig.groups[randomGroupIndex%groupsSize]

				currPlayer = playersWithoutGroup[currPlayerIndex];
				currGroup.addPlayer(playerModelBridge, currPlayer);

				currPlayerFitness = fitAlg.calculate(playerModelBridge, currPlayer, currGroup.interactionsProfile, regAlg)
				currFitness += currPlayerFitness

				playersWithoutGroup = numpy.delete(playersWithoutGroup, currPlayerIndex)
				playersWithoutGroupSize = len(playersWithoutGroup)

			playerSize = len(playerIds)
			currGroups = newConfig.groups
			currGroupsSize = len(currGroups)
			# self.configSizeFreqs[currGroupsSize]+=1
			for s in range(currGroupsSize):
				currGroup = currGroups[s]
				# self.groupSizeFreqs[len(currGroup.players)]+=1

			if (currFitness > currMaxFitness):
				bestConfig = newConfig
				currMaxFitness = currFitness	
		
		self.updateMetrics(bestConfig)
		return bestConfig



class EvolutionaryConfigsGen(ConfigsGenAlg):
	def organize(self, players, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):

		bestConfig = AdaptationConfiguration()
		currMaxFitness = -math.inf

		# generate several random groups, calculate their fitness and select best one
		adaptG = AdaptationGroup(InteractionsProfile(0.33, 0.33, 0.33), players )
		updateMetrics(bestConfig)
		return bestConfig

