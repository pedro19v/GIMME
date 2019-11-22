import numpy
import math
from abc import ABC, abstractmethod
from AdaptationStructs import *
from AuxStructs.InteractionsProfile import InteractionsProfile 

class ConfigsGenAlg(ABC):

	def __init__(self):
		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}
		super().__init__()

	def randomProfileGenerator(self, group):
		# generate learning profile
		profile = InteractionsProfile()
		profile.K_cp = numpy.random.uniform(0, 1)
		profile.K_i = numpy.random.uniform(0, 1)
		profile.K_mh = numpy.random.uniform(0, 1)
		profile.K_pa = numpy.random.uniform(0, 1)

		# total = profile.K_cp +profile.K_i +profile.K_mh +profile.K_pa 

		# profile.K_cp /= total
		# profile.K_i /= total
		# profile.K_mh /= total
		# profile.K_pa /= total

		return profile

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





# class PersonalityBasedConfigsGen(RandomConfigsGen):
# 	def personalityBasedProfileGenerator(self, group):
# 		# generate learning profile
# 		profile = InteractionsProfile()
# 		profile.K_cp = numpy.random.normal(group.avgPersonality.K_cp, self.variation)
# 		profile.K_i = numpy.random.normal(group.avgPersonality.K_i, self.variation)
# 		profile.K_mh = numpy.random.normal(group.avgPersonality.K_mh, self.variation)
# 		profile.K_pa = numpy.random.normal(group.avgPersonality.K_pa, self.variation)
# 		return profile

# 	def __init__(self, variation):
# 		RandomConfigsGen.__init__(self)
# 		self.profileGenerator = self.personalityBasedProfileGenerator
# 		self.variation = variation

# class SimOptimalConfigsGen(RandomConfigsGen):
# 	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		
# 		bestConfig = AdaptationConfiguration()
# 		currMaxFitness = 0.0

# 		for j in range(numberOfConfigChoices):
		

class EvolutionaryConfigsGen(ConfigsGenAlg):
	def __init__(self):
		super().__init__()
		self.populationInited = False
		
	def updatePopulation(self, numPlayers, maxNumGroups, numberOfConfigChoices):
		self.currPopulation = [[numpy.random.uniform(0, maxNumGroups) for x in range(numPlayers)] for y in range(numberOfConfigChoices)]
		self.currPopulationFitnesses = [0 for x in range(numPlayers)]

		self.currProfiles = [[ [numpy.random.uniform(0, 1), numpy.random.uniform(0, 1), numpy.random.uniform(0, 1), numpy.random.uniform(0, 1)] for x in range(maxNumGroups)] for y in range(numberOfConfigChoices)]


	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		print("Here4")
		
		bestConfig = AdaptationConfiguration()

		numPlayers = len(playerIds)

		if(numPlayers < minNumberOfPlayersPerGroup):
			return bestConfig

		currMaxFitness = -float("inf")

		minNumGroups = math.ceil(len(playerIds) / maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / minNumberOfPlayersPerGroup)

		#build first population
		if(self.populationInited == False):
			self.updatePopulation(numPlayers, maxNumGroups, numberOfConfigChoices)
			self.populationInited = True
		

		for config in range(numberOfConfigChoices):
			if(numpy.random.uniform(0,1) < 0.1):
				#mutation
				for i in range(self.numMutations):
					self.currPopulation[config][numpy.random.random_integers(0, numPlayers)] = numpy.random.random_integers(0, maxNumGroups)
					for profile in range(maxNumGroups):
						self.currProfiles[config][numpy.random.random_integers(0, maxNumGroups)][random(0, 4)] = numpy.random.uniform(0, 1)
			else:
				#crossover
				# 2 crossovers differentes 

				# determine mate
				mate = numpy.random.random_integers(0, numberOfConfigChoices)

				# group crossovers
				crossoverPoint = numpy.random.random_integers(0, numPlayers)
				print(self.currPopulation[config][:crossoverPoint])
				parentConfig = config
				self.currPopulation[config] = self.currPopulation[parentConfig][:crossoverPoint].append(self.currPopulation[mate][crossoverPoint:])
				self.currPopulation[mate] = self.currPopulation[mate][:crossoverPoint].append(self.currPopulation[parentConfig][crossoverPoint:])

				# GIP or inside of GIP crossover
				crossoverPoint = numpy.random.random_integers(0, numPlayers)
				self.currProfiles[config][group] = self.currProfiles[config][group][:crossoverPoint].append(self.currProfiles[config][group][crossoverPoint:])


		#G->P
		print(currPopulation, default=lambda o: o.__dict__, sort_keys=True)


		#fitness
		for c in range(numberOfConfigChoices):
			config = self.currPopulation[c]
			for p in range(numPlayers):
				group = config[p]
				currProfile = self.currProfiles[c][group]
				currPlayerFitness = fitAlg.calculate(playerModelBridge, p, currProfile, regAlg)
				currPopulationFitnesses[currPlayer] += currPlayerFitness

		#selection

		pass


class OptimalPracticalConfigsGen(ConfigsGenAlg):

	def __init__(self):
		super().__init__()
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
				numGroups = numpy.random.randint(minNumGroups, maxNumGroups)
			else: # players length is 1
				numGroups = maxNumGroups + 1

			# generate min groups
			playersWithoutGroupSize = 0
			for j in range(numGroups):
				currGroup = AdaptationGroup()

				# add min number of players to the group
				for s in range(min(playersWithoutGroupSize, minNumberOfPlayersPerGroup)):
					playersWithoutGroupSize = len(playersWithoutGroup)
					currPlayerIndex = numpy.random.randint(0, playersWithoutGroupSize - 1)
					currPlayerID = playersWithoutGroup[currPlayerIndex]
					currGroup.addPlayer(playerModelBridge, currPlayerID)

					del playersWithoutGroup[currPlayerIndex]

				newConfig.groups.append(currGroup)

			# append the rest
			playersWithoutGroupSize = len(playersWithoutGroup)
			while playersWithoutGroupSize > 0:

				randomGroupIndex = numpy.random.randint(0, len(newConfig.groups) - 1)

				currPlayerIndex = 0;
				if (playersWithoutGroupSize > 1):
					currPlayerIndex = numpy.random.randint(0, playersWithoutGroupSize - 1)
				else:
					currPlayerIndex = 0

				currGroup = newConfig.groups[randomGroupIndex]
				groupsSize = len(newConfig.groups)

				while (len(currGroup.playerIds) > (maxNumberOfPlayersPerGroup - 1)):
					randomGroupIndex += 1
					currGroup = newConfig.groups[randomGroupIndex%groupsSize]

				currPlayer = playersWithoutGroup[currPlayerIndex]
				currGroup.addPlayer(playerModelBridge, currPlayer)

				del playersWithoutGroup[currPlayerIndex]
				playersWithoutGroupSize = len(playersWithoutGroup)


			playerSize = len(playerIds)
			currGroups = newConfig.groups
			currGroupsSize = len(currGroups)

			# generate profiles
			for group in currGroups:
				# generate learning profile
				profile = InteractionsProfile()
				for currPlayer in group.playerIds:
					personality = playerModelBridge.getPlayerPersonality(currPlayer)
					profile.K_cp += personality.K_cp/currGroupsSize
					profile.K_i += personality.K_i/currGroupsSize
					profile.K_mh += personality.K_mh/currGroupsSize
					profile.K_pa += personality.K_pa/currGroupsSize

				group.profile = profile

				for currPlayer in group.playerIds:
					currPlayerFitness = fitAlg.calculate(playerModelBridge, currPlayer, group.profile, regAlg)
					currFitness += currPlayerFitness

			# print(json.dumps(group, default=lambda o: o.__dict__, sort_keys=True))
			if (currFitness > currMaxFitness):
				bestConfig = newConfig
				currMaxFitness = currFitness
				
		# print("---------------------------")
		# for group in bestConfig.groups:
		# 	print(group.playerIds)
		# print(json.dumps(bestConfig, default=lambda o: o.__dict__, sort_keys=True))
		self.updateMetrics(bestConfig)
		return bestConfig



class GIMMEConfigsGen(ConfigsGenAlg):

	def __init__(self):
		super().__init__()
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
				numGroups = numpy.random.randint(minNumGroups, maxNumGroups)
			else: # players length is 1
				numGroups = maxNumGroups + 1

			# generate min groups
			playersWithoutGroupSize = 0
			for j in range(numGroups):
				currGroup = AdaptationGroup()

				# add min number of players to the group
				for s in range(min(playersWithoutGroupSize, minNumberOfPlayersPerGroup)):
					playersWithoutGroupSize = len(playersWithoutGroup)
					currPlayerIndex = numpy.random.randint(0, playersWithoutGroupSize - 1)
					currPlayerID = playersWithoutGroup[currPlayerIndex]
					currGroup.addPlayer(playerModelBridge, currPlayerID)

					del playersWithoutGroup[currPlayerIndex]

				newConfig.groups.append(currGroup)

			# append the rest
			playersWithoutGroupSize = len(playersWithoutGroup)
			while playersWithoutGroupSize > 0:

				randomGroupIndex = numpy.random.randint(0, len(newConfig.groups) - 1)

				currPlayerIndex = 0;
				if (playersWithoutGroupSize > 1):
					currPlayerIndex = numpy.random.randint(0, playersWithoutGroupSize - 1)
				else:
					currPlayerIndex = 0

				currGroup = newConfig.groups[randomGroupIndex]
				groupsSize = len(newConfig.groups)

				while (len(currGroup.playerIds) > (maxNumberOfPlayersPerGroup - 1)):
					randomGroupIndex += 1
					currGroup = newConfig.groups[randomGroupIndex%groupsSize]

				currPlayer = playersWithoutGroup[currPlayerIndex]
				currGroup.addPlayer(playerModelBridge, currPlayer)

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
				
		# print("---------------------------")
		# for group in bestConfig.groups:
		# 	print(group.playerIds)
		# print(json.dumps(bestConfig, default=lambda o: o.__dict__, sort_keys=True))
		self.updateMetrics(bestConfig)
		return bestConfig


class RandomConfigsGen(ConfigsGenAlg):

	def __init__(self):
		super().__init__()
		self.profileGenerator = self.randomProfileGenerator

	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):
		playersWithoutGroup = playerIds.copy()
		playersWithoutGroupSize = 0
		randomConfig = AdaptationConfiguration()


		minNumGroups = math.ceil(len(playerIds) / maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / minNumberOfPlayersPerGroup)

		if(minNumGroups < maxNumGroups):
			numGroups = numpy.random.randint(minNumGroups, maxNumGroups)
		else: # players length is 1
			numGroups = maxNumGroups + 1


		if(minNumGroups < maxNumGroups):
			numGroups = numpy.random.randint(minNumGroups, maxNumGroups)
		else: # players length is 1
			numGroups = maxNumGroups + 1


		# generate min groups
		for j in range(numGroups):
			currGroup = AdaptationGroup()
			currGroup.profile = self.profileGenerator(currGroup)

			# add min number of players to the group
			for s in range(min(playersWithoutGroupSize, minNumberOfPlayersPerGroup)):
				playersWithoutGroupSize = len(playersWithoutGroup)
				currPlayerIndex = numpy.random.randint(0, playersWithoutGroupSize - 1)
				currPlayerID = playersWithoutGroup[currPlayerIndex]
				currGroup.addPlayer(playerModelBridge, currPlayerID)

				del playersWithoutGroup[currPlayerIndex]
	
			randomConfig.groups.append(currGroup)

		# append the rest
		playersWithoutGroupSize = len(playersWithoutGroup)
		while playersWithoutGroupSize > 0:

			randomGroupIndex = numpy.random.randint(0, len(randomConfig.groups) - 1)

			currPlayerIndex = 0;
			if (playersWithoutGroupSize > 1):
				currPlayerIndex = numpy.random.randint(0, playersWithoutGroupSize - 1)
			else:
				currPlayerIndex = 0

			currGroup = randomConfig.groups[randomGroupIndex]
			groupsSize = len(randomConfig.groups)

			while (len(currGroup.playerIds) > (maxNumberOfPlayersPerGroup - 1)):
				randomGroupIndex += 1
				currGroup = randomConfig.groups[randomGroupIndex%groupsSize]

			currPlayer = playersWithoutGroup[currPlayerIndex]
			currGroup.addPlayer(playerModelBridge, currPlayer)

			del playersWithoutGroup[currPlayerIndex]
			playersWithoutGroupSize = len(playersWithoutGroup)


		# print(json.dumps(randomConfig, default=lambda o: o.__dict__, sort_keys=True))
		return randomConfig