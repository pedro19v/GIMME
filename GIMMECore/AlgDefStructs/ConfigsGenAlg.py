import random
import math
import copy
from abc import ABC, abstractmethod
from AdaptationStructs import *
from InteractionsProfile import InteractionsProfile 

import matplotlib.pyplot as plt


class ConfigsGenAlg(ABC):

	def __init__(self):
		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}
		super().__init__()

	def reset(self):
		pass

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
	def __init__(self, numMutations=4, numFitSurvivors=None):
		super().__init__()
		self.populationInited = False
		self.numMutations = numMutations
		self.numFitSurvivors = numFitSurvivors

	def reset(self):
		self.currPopulation = []
		self.currProfiles = []
		self.populationInited = False

	def fitnessSort(self, elem):
		return elem[0]["fitness"]

	def updatePopulation(self, playerIds, numPlayers, maxNumGroups, numberOfConfigChoices):
		# represented as simple genotypes
		self.currPopulation = [ {'config': [], 'fitness': 0.0}  for y in range(numberOfConfigChoices)]
		for individual in self.currPopulation:
			individual["config"] = [[playerIds[x], random.randint(0, maxNumGroups-1)] for x in range(numPlayers)]

		self.currProfiles = [ {'config': [], 'fitness': 0.0} for y in range(numberOfConfigChoices)]
		for individual in self.currProfiles:
			individual["config"] = [InteractionsProfile(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) for x in range(maxNumGroups)]

	def organize(self, playerModelBridge, playerIds, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, regAlg, fitAlg):

		if(self.numFitSurvivors == None):
			self.numFitSurvivors = math.ceil(numberOfConfigChoices/2)
		
		bestConfig = AdaptationConfiguration()
		numPlayers = len(playerIds)

		if(numPlayers < minNumberOfPlayersPerGroup):
			return bestConfig

		currMaxFitness = -float("inf")

		minNumGroups = math.ceil(len(playerIds) / maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / minNumberOfPlayersPerGroup)

		#build first population
		if(self.populationInited == False):
			self.updatePopulation(playerIds, numPlayers, maxNumGroups, numberOfConfigChoices)
			self.populationInited = True
		

		for config in range(numberOfConfigChoices):
			if(random.uniform(0,1) < 0.1):
				#mutation (exploration)
				for i in range(self.numMutations):
					# alter random individual's group
					self.currPopulation[config]["config"][random.randint(0, numPlayers-1)][1] = random.randint(0, maxNumGroups-1)
					
					# alter random group's GIP
					for profile in range(maxNumGroups):
						randomGroup = random.randint(0, maxNumGroups-1)
						intProfileToChange = self.currProfiles[config]["config"][randomGroup]

						randomNum = random.randint(0, 3)
						if(randomNum==0):
							intProfileToChange.K_cp = random.uniform(0, 1)
						elif(randomNum==1):
							intProfileToChange.K_pa = random.uniform(0, 1)
						elif(randomNum==2):
							intProfileToChange.K_mh = random.uniform(0, 1)
						elif(randomNum==3):
							intProfileToChange.K_i = random.uniform(0, 1)
						
						self.currProfiles[config]["config"][randomGroup] = intProfileToChange
			else:
				#crossover (exploitation)
				# 2 different crossovers - config and GIP 

				# determine mate
				mate = random.randint(0, numberOfConfigChoices-1)

				# config crossovers
				crossoverPoint = random.randint(0, numPlayers-1)

				parentConfig = config
				tempConfig = self.currPopulation[parentConfig]["config"][:crossoverPoint]+self.currPopulation[mate]["config"][crossoverPoint:]
				self.currPopulation[mate]["config"] = self.currPopulation[mate]["config"][:crossoverPoint]+self.currPopulation[parentConfig]["config"][crossoverPoint:]
				self.currPopulation[config]["config"] = tempConfig

				# GIP or inside of GIP crossover
				# crossoverPoint = random.randint(0, numPlayers-1)
				tempConfig = (self.currProfiles[config]["config"][:crossoverPoint] + self.currProfiles[mate]["config"][crossoverPoint:])
				self.currProfiles[mate]["config"] = (self.currProfiles[mate]["config"][:crossoverPoint] + self.currProfiles[config]["config"][crossoverPoint:])
				self.currProfiles[config]["config"] = tempConfig
				
		# print(json.dumps(self.currProfiles, default=lambda o: o.__dict__, sort_keys=True))
		# input()

		#calc fitness after KNN for regression
		for c in range(numberOfConfigChoices):
			totalFitness = 0
			config = self.currPopulation[c]["config"]
			for p in range(numPlayers):
				group = config[p][1]
				currProfile = self.currProfiles[c]["config"][group]
				predictedState = regAlg.predict(playerModelBridge, currProfile, p)
				currPlayerFitness = fitAlg.calculate(playerModelBridge, predictedState)
				
				# print(json.dumps(group, default=lambda o: o.__dict__, sort_keys=True))
				# print(json.dumps(currProfile, default=lambda o: o.__dict__, sort_keys=True))
				totalFitness += currPlayerFitness

				
				self.currPopulation[c]["fitness"] += currPlayerFitness
				self.currProfiles[c]["fitness"] = self.currPopulation[c]["fitness"]

			# 	print("-----------------------------")
			# print(self.currPopulation[c]["fitness"])
			# print("----------------------------------------------------------")
				
				# if(currFitness > currMaxFitness):
				# 	currMaxFitness = currFitness
				# 	if(bestConfig != c):
				# 		bestConfig = c

				# print(p)
				# print(playerModelBridge)
				# print(json.dumps(currProfile, default=lambda o: o.__dict__, sort_keys=True))
				# print(json.dumps(predictedState, default=lambda o: o.__dict__, sort_keys=True))
				# input()

			
		
		# print(self.currPopulation)
		# input()
		self.currPopulation, self.currProfiles = zip(*sorted(zip(self.currPopulation, self.currProfiles), key=self.fitnessSort))
		self.currPopulation = [a for a in self.currPopulation] #sort by column 1 which is the actual fitness
		self.currProfiles = [a for a in self.currProfiles] #sort by column 1 which is the actual fitness
		# print(self.currPopulation)
		# input()

		#selection by elitition
		fitSurvivorsPop = self.currPopulation[self.numFitSurvivors:]
		self.currPopulation = fitSurvivorsPop + fitSurvivorsPop

		fitSurvivorsProf = self.currProfiles[self.numFitSurvivors:]
		self.currProfiles = fitSurvivorsProf + fitSurvivorsProf


		# print(self.currPopulation)
		for c in range(numberOfConfigChoices):
			self.currPopulation[c]["fitness"] = 0.0
			self.currProfiles[c]["fitness"] = 0.0

		# calc Genotype->Phenotype of best config(coalition) and return
		bestConfig = AdaptationConfiguration()
		bestConfig.groups = [AdaptationGroup() for i in range(maxNumGroups)]

		bestConfigGenotype = self.currPopulation[-1]["config"]
		bestProfilesGenotype = self.currProfiles[-1]["config"]


		for gene in bestConfigGenotype:
			bestConfig.groups[gene[1]].addPlayer(playerModelBridge, gene[0])
			bestConfig.groups[gene[1]].profile = bestProfilesGenotype[gene[1]]

			# print(json.dumps(bestConfig.groups[gene[1]].profile, default=lambda o: o.__dict__, sort_keys=True))
			# input()

		# print(json.dumps(bestConfig, default=lambda o: o.__dict__, sort_keys=True))
		# input()
		return bestConfig


class OptimalPracticalConfigsGen(ConfigsGenAlg):

	def __init__(self, simulationFunc):
		super().__init__()
		self.profileGenerator = self.randomProfileGenerator

		self.simulationFunc = simulationFunc
		self.currIteration = 0


	def updateCurrIteration(self, newCurrIteration):
		self.currIteration = newCurrIteration

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

				newConfig.groups = numpy.append(newConfig.groups,currGroup)
				# newConfig.groups.append(currGroup)

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

					currState = playerModelBridge.getPlayerCurrState(currPlayer)
					newState = self.simulationFunc(currState, playerModelBridge, currPlayer, group.profile, self.currIteration)
		
					currPlayerFitness = fitAlg.calculate(playerModelBridge, newState)
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

				newConfig.groups = numpy.append(newConfig.groups,currGroup)
				# newConfig.groups.append(currGroup)

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
					predictedState = regAlg.predict(playerModelBridge, group.profile, currPlayer)
					
					currPlayerFitness = fitAlg.calculate(playerModelBridge, predictedState)
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
	
			randomConfig.groups = numpy.append(randomConfig.groups,currGroup)
			# randomConfig.groups.append(currGroup)

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