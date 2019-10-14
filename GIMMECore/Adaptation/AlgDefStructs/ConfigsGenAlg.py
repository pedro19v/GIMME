from abc import ABC, abstractmethod
from AuxStructs.RandomGen import * 
from AuxStructs.InteractionsProfile import InteractionsProfile 

class ConfigsGenAlg(ABC):

# public:
	def __init__(self):
		self.groupSizeFreqs = numpy.empty(0)
		self.configSizeFreqs = numpy.empty(0)
		super().__init__()

	def init(self, playerIDs):
		playersSize = len(playerIDs);
		self.groupSizeFreqs = numpy.empty(playersSize + 1)
		self.configSizeFreqs = numpy.empty(playersSize + 1)

	@abstractmethod
	def organize(self, players, numberOfConfigChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, utilities, regAlg, fitAlg):
		pass

	def updateMetrics(self, generatedConfig):
		self.configSizeFreqs[len(generatedConfig.groups)]+=1
		for group in generatedConfig.groups:
			self.groupSizeFreqs[group.players.size()]+=1



class RandomConfigsGen(ConfigsGenAlg):

	def organize(self, players, numberOfConfigChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, utilities, regAlg, fitAlg):
		bestConfig = AdaptationConfiguration()
		currMaxFitness = -1.0

		# generate several random groups, calculate their fitness and select the best one
		for j in range(numberOfConfigChoices):
			lastProfile = False
			currFitness = 0.0
			playersWithoutGroup = players
			newConfig = AdaptationConfiguration()

			minNumGroups = ceil(len(players) / maxNumberOfPlayersPerGroup);
			maxNumGroups = floor(len(players) / minNumberOfPlayersPerGroup);
			numGroups = randomGen.randIntBetween(minNumGroups, maxNumGroups);

			# generate min groups
			playersWithoutGroupSize = 0
			for j in range(numGroups):
				currGroup = AdaptationGroup();

				# generate learning profile
				newRand1 = randomGen.randBetween(0, 1)
				newRand2 = randomGen.randBetween(0, 1)
				newRand3 = randomGen.randBetween(0, 1)

				newRandSum = newRand1 + newRand2 + newRand3;

				profile = InteractionsProfile();
				profile.K_cl = newRand1 / newRandSum;
				profile.K_cp = newRand2 / newRandSum;
				profile.K_i = newRand3 / newRandSum;
				currGroup.interactionsProfile = profile;


				for s in range(minNumberOfPlayersPerGroup):
					playersWithoutGroupSize = len(playersWithoutGroup)
					currPlayerIndex = randomGen.randIntBetween(0, playersWithoutGroupSize - 1)

					currPlayerID = playersWithoutGroup[currPlayerIndex]
					currGroup.addPlayer(currPlayerID)

					currPlayerFitness = fitAlg.calculate(currPlayerID, currGroup.interactionsProfile, regAlg)
					currFitness += currPlayerFitness

					playersWithoutGroup = numpy.delete(playersWithoutGroup, currPlayerIndex)
				
				newConfig.groups = numpy.append(newConfig.groups, currGroup)

			playersWithoutGroupSize = len(playersWithoutGroup);
			
			while playersWithoutGroupSize > 0:
				randomGroupIndex = randomGen.randIntBetween(0, len(newConfig.groups) - 1)

				currPlayerIndex = 0;
				if (playersWithoutGroupSize > 1):
					currPlayerIndex = randomGen.randIntBetween(0, playersWithoutGroupSize - 1)

				currGroup = newConfig.groups[randomGroupIndex];
				groupsSize = len(newConfig.groups);
				while (len(currGroup) > maxNumberOfPlayersPerGroup - 1):
					randomGroupIndex+=1
					currGroup = newConfig.groups[randomGroupIndex%groupsSize]

				currPlayer = playersWithoutGroup[currPlayerIndex];
				currGroup.addPlayer(currPlayer);

				currPlayerFitness = fitAlg.calculate(currPlayer, currGroup.interactionsProfile, regAlg)
				currFitness += currPlayerFitness

				playersWithoutGroup = numpy.delete(playersWithoutGroup, currPlayerIndex)
				playersWithoutGroupSize = len(playersWithoutGroup)

			playerSize = len(players)
			currGroups = newConfig.groups
			currGroupsSize = len(currGroups)
			self.configSizeFreqs[currGroupsSize]+=1
			for s in range(currGroupsSize):
				currGroup = currGroups[s]
				self.groupSizeFreqs[len(currGroup.players)]+=1

			if (currFitness > currMaxFitness):
				bestConfig = newConfig
				currMaxFitness = currFitness	
		
		self.updateMetrics(bestConfig)
		return bestConfig



class EvolutionaryConfigsGen(ConfigsGenAlg):
	def organize(self, players, numberOfConfigChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, utilities, regAlg, fitAlg):

		bestConfig = AdaptationConfiguration()
		currMaxFitness = -math.inf

		# generate several random groups, calculate their fitness and select best one
		adaptG = AdaptationGroup(InteractionsProfile(0.33, 0.33, 0.33), players )
		updateMetrics(bestConfig)
		return bestConfig

