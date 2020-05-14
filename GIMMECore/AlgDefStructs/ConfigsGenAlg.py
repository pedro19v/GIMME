import random
import math
import copy
from abc import ABC, abstractmethod
from ..InteractionsProfile import InteractionsProfile 
from ..PlayerStructs import *
from ..AlgDefStructs.RegressionAlg import *
import matplotlib.pyplot as plt


class ConfigsGenAlg(ABC):

	def __init__(self, playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = None, minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5):
		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}
		
		if(minNumberOfPlayersPerGroup > maxNumberOfPlayersPerGroup):
			raise ValueError('The min number of players per group cannot be higher than the max!') 
		
		if preferredNumberOfPlayersPerGroup == None:
			self.maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup
			self.minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup
		else:
			self.maxNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup
			self.minNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup

		self.playerModelBridge = playerModelBridge
		self.interactionsProfileTemplate = interactionsProfileTemplate

	def reset(self):
		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}

	def randomProfileGenerator(self):
		# generate learning profile
		profile = self.interactionsProfileTemplate.generateCopy()
		profile.reset()

		for key in profile.dimensions:
			profile.dimensions[key] = random.uniform(0.0, 1.0)
		profile.normalize()

		return profile


	def randomConfigGenerator(self, playerIds, minNumGroups, maxNumGroups):
		
		returnedConfig = []

		if(len(playerIds) < self.minNumberOfPlayersPerGroup):
			print("number of players is lower than the minimum number of players per group!")
			return bestGroups
			
		# generate random config
		playersWithoutGroup = playerIds.copy()

		if(minNumGroups < maxNumGroups):
			numGroups = numpy.random.randint(minNumGroups, maxNumGroups)
		else: # players length is 1
			numGroups = maxNumGroups

		# generate min num players for each group
		playersWithoutGroupSize = len(playersWithoutGroup)
		for g in range(numGroups):
			currGroup = []

			if(playersWithoutGroupSize < 1):
				break

			# add min number of players to the group
			for p in range(self.minNumberOfPlayersPerGroup):
				currPlayerIndex = random.randint(0, len(playersWithoutGroup) - 1)
				currPlayerID = playersWithoutGroup[currPlayerIndex]
				currGroup.append(currPlayerID)
				del playersWithoutGroup[currPlayerIndex]
			
			returnedConfig.append(currGroup)
		
		# append the rest
		playersWithoutGroupSize = len(playersWithoutGroup)
		while playersWithoutGroupSize > 0:
			currPlayerIndex = 0;
			if (playersWithoutGroupSize > 1):
				currPlayerIndex = random.randint(0, playersWithoutGroupSize - 1)
			else:
				currPlayerIndex = 0
			currPlayerID = playersWithoutGroup[currPlayerIndex]

			groupsSize = len(returnedConfig)

			availableGroups = returnedConfig.copy()
			while (len(currGroup) > (self.maxNumberOfPlayersPerGroup - 1)):
				if(len(availableGroups) < 1):
					currGroup = random.choice(returnedConfig)
					break
				currGroup = random.choice(availableGroups)
				availableGroups.remove(currGroup)

			currGroup.append(currPlayerID)

			del playersWithoutGroup[currPlayerIndex]
			playersWithoutGroupSize = len(playersWithoutGroup)

		return returnedConfig



	@abstractmethod
	def organize(self):
		pass

	def updateMetrics(self, generatedConfig):
		if(self.configSizeFreqs.get(len(generatedConfig))):
			self.configSizeFreqs[len(generatedConfig)]+=1
		else:
			self.configSizeFreqs[len(generatedConfig)]=1

		for group in generatedConfig:
			if(self.configSizeFreqs.get(len(group))):
				self.configSizeFreqs[len(group)]+=1
			else:
				self.configSizeFreqs[len(group)]=1



class RandomConfigsGen(ConfigsGenAlg):

	def __init__(self, playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = None, minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5):
		super().__init__(playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)
		self.profileGenerator = self.randomProfileGenerator

	def organize(self):
		playerIds = self.playerModelBridge.getAllPlayerIds() 
		minNumGroups = math.ceil(len(playerIds) / self.maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / self.minNumberOfPlayersPerGroup)
		
		newConfigProfiles = []
		newAvgCharacteristics = []
		
		newGroups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
		newConfigSize = len(newGroups)		
		# generate profiles
		for groupI in range(newConfigSize):
			group = newGroups[groupI]
			groupSize = len(group)
			
			# generate random profile
			profile = self.profileGenerator()
			newConfigProfiles.append(profile)

			currAvgCharacteristics = PlayerCharacteristics()
			currAvgCharacteristics.reset()
			for currPlayer in group:
				currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
				currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
				currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
			currAvgCharacteristics.profile = profile
			newAvgCharacteristics.append(currAvgCharacteristics)

		self.updateMetrics(newGroups)
		return {"groups": newGroups, "profiles": newConfigProfiles, "avgCharacteristics": newAvgCharacteristics}


class SimpleConfigsGen(ConfigsGenAlg):

	def __init__(self, playerModelBridge, interactionsProfileTemplate, regAlg = None, persEstAlg = None, numberOfConfigChoices = 100, preferredNumberOfPlayersPerGroup = None, minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5, qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5), allPlayersInited = True):
		super().__init__(playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)
		self.regAlg = regAlg
		self.persEstAlg = persEstAlg
		self.numberOfConfigChoices = numberOfConfigChoices
		self.profileGenerator = self.randomProfileGenerator
		
		self.qualityWeights = qualityWeights

		self.allPlayersInited = allPlayersInited
		self.configsGenAlgIniter = RandomConfigsGen(playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		if(regAlg==None):
			regAlg = KNNRegression(playerModelBridge, 5)

		if(persEstAlg==None):
			persEstAlg = SimplePersonalityEstAlg(playerModelBridge, self.calcQuality)

	def areAllPlayersInited(self, allPlayersInited):
		self.allPlayersInited = allPlayersInited


	def calcQuality(self, state):
		return self.qualityWeights.ability*state.characteristics.ability + self.qualityWeights.engagement*state.characteristics.engagement
			
	def organize(self):
		playerIds = self.playerModelBridge.getAllPlayerIds() 
		minNumGroups = math.ceil(len(playerIds) / self.maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / self.minNumberOfPlayersPerGroup)

		currMaxQuality = -float("inf")

		bestGroups = []
		bestConfigProfiles = []
		bestAvgCharacteristics = []


		# estimate personalities
		self.persEstAlg.updateEstimates()

		# generate several random groups, calculate their fitness and select the best one
		for i in range(self.numberOfConfigChoices):
			
			newGroups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
			newConfigSize = len(newGroups)
			currQuality = 0.0
			newConfigProfiles = []
			newAvgCharacteristics = []

			# generate profiles
			for groupI in range(newConfigSize):
				group = newGroups[groupI]
				groupSize = len(group)

				# generate profile as average of the personalities estimates
				profile = self.interactionsProfileTemplate.generateCopy()
				profile.reset()
				
				for currPlayer in group:
					personality = self.playerModelBridge.getPlayerPersonalityEst(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += personality.dimensions[dim]/newConfigSize
					profile.normalize()
				newConfigProfiles.append(profile)


				# calculate fitness and average state
				currAvgCharacteristics = PlayerCharacteristics()
				currAvgCharacteristics.reset()
				for currPlayer in group:

					currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
					currState.profile = profile

					currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
					currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
				
					predictedIncreases = self.regAlg.predict(profile, currPlayer)
					currQuality += self.calcQuality(predictedIncreases)

				newAvgCharacteristics.append(currAvgCharacteristics)
			
			if (currQuality > currMaxQuality):
				bestGroups = newGroups
				bestConfigProfiles = newConfigProfiles
				bestAvgCharacteristics = newAvgCharacteristics
				currMaxQuality = currQuality

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}


class AccurateConfigsGen(ConfigsGenAlg):

	def __init__(self, playerModelBridge, interactionsProfileTemplate, simulationFunc, numberOfConfigChoices = 100, preferredNumberOfPlayersPerGroup = None, minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5, qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5)):
		super().__init__(playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)
		self.profileGenerator = self.randomProfileGenerator
		self.numberOfConfigChoices = numberOfConfigChoices
		self.simulationFunc = simulationFunc
		self.currIteration = 0

		self.qualityWeights = qualityWeights


	def updateCurrIteration(self, newCurrIteration):
		self.currIteration = newCurrIteration

	def organize(self):
		playerIds = self.playerModelBridge.getAllPlayerIds() 
		minNumGroups = math.ceil(len(playerIds) / self.maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / self.minNumberOfPlayersPerGroup)

		currMaxQuality = -float("inf")

		bestGroups = []
		bestConfigProfiles = []
		bestAvgCharacteristics = []

		# generate several random groups, calculate their fitness and select the best one
		for i in range(self.numberOfConfigChoices):
			
			newGroups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
			newConfigSize = len(newGroups)
			currQuality = 0.0
			newConfigProfiles = []
			newAvgCharacteristics = []

			# generate profiles
			for groupI in range(newConfigSize):
				group = newGroups[groupI]
				groupSize = len(group)

				# generate profile as average of the personalities
				profile = self.interactionsProfileTemplate.generateCopy()
				profile.reset()
				
				for currPlayer in group:
					personality = self.playerModelBridge.getPlayerRealPersonality(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += personality.dimensions[dim]/newConfigSize
					profile.normalize()
				newConfigProfiles.append(profile)


				# calculate fitness and average state
				currAvgCharacteristics = PlayerCharacteristics()
				currAvgCharacteristics.reset()
				for currPlayer in group:
					currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
					currState.profile = profile

					currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
					currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize

					newState = self.simulationFunc(self.playerModelBridge, currState, currPlayer, profile, self.currIteration)
		
					increases = PlayerState()
					increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
				
					currQuality += self.qualityWeights.ability*increases.characteristics.ability + self.qualityWeights.engagement*increases.characteristics.engagement
				newAvgCharacteristics.append(currAvgCharacteristics)
			
			if (currQuality > currMaxQuality):
				bestGroups = newGroups
				bestConfigProfiles = newConfigProfiles
				bestAvgCharacteristics = newAvgCharacteristics
				currMaxQuality = currQuality

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}



class EvolutionaryConfigsGen(ConfigsGenAlg):
	def __init__(self, playerModelBridge, interactionsProfileTemplate, regAlg = None, numberOfConfigChoices = 100, preferredNumberOfPlayersPerGroup = None, minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5, fitnessWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5), numMutations=4, probOfMutation=0.1, numFitSurvivors=None):
		super().__init__(playerModelBridge, interactionsProfileTemplate, preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)
		self.regAlg = regAlg
		self.numberOfConfigChoices = numberOfConfigChoices

		self.populationInited = False
		self.numMutations = numMutations
		self.numFitSurvivors = numFitSurvivors
		self.probOfMutation = probOfMutation

		if(regAlg==None):
			regAlg = KNNRegression(playerModelBridge, 5)

		self.fitnessWeights = fitnessWeights

	def reset(self):
		super().reset()
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

	def organize(self):
		playerIds = self.playerModelBridge.getAllPlayerIds() 

		if(self.numFitSurvivors == None):
			self.numFitSurvivors = math.ceil(self.numberOfConfigChoices/2)
		
		numPlayers = len(playerIds)
		if(numPlayers < self.minNumberOfPlayersPerGroup):
			return bestConfig
		minNumGroups = math.ceil(numPlayers / self.maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(numPlayers / self.minNumberOfPlayersPerGroup)

		currMaxQuality = -float("inf")

		#build first population
		if(self.populationInited == False):
			self.updatePopulation(playerIds, numPlayers, maxNumGroups, self.numberOfConfigChoices)
			self.populationInited = True
		
		for config in range(self.numberOfConfigChoices):
			if(random.uniform(0.0,1.0) < self.probOfMutation):
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
				mate = random.randint(0, self.numberOfConfigChoices-1)

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
				
		#calc fitness after KNN for regression
		for c in range(self.numberOfConfigChoices):
			totalFitness = 0
			config = self.currPopulation[c]["config"]
			for p in config:
				group = p[1]
				playerId = p[0]
				profile = self.currProfiles[c]["config"][group]
				
				predictedIncreases = self.regAlg.predict(profile, playerId)
				self.currPopulation[c]["fitness"] += self.fitnessWeights.ability*predictedIncreases.characteristics.ability + self.fitnessWeights.engagement*predictedIncreases.characteristics.engagement

			self.currProfiles[c]["fitness"] = self.currPopulation[c]["fitness"]

		self.currPopulation, self.currProfiles = zip(*sorted(zip(self.currPopulation, self.currProfiles), key=self.fitnessSort))
		self.currPopulation = [a for a in self.currPopulation] #sort by column 1 which is the actual fitness
		self.currProfiles = [a for a in self.currProfiles] #sort by column 1 which is the actual fitness
		
		#selection by elitition
		fitSurvivorsPop = self.currPopulation[self.numFitSurvivors:]
		self.currPopulation = fitSurvivorsPop + fitSurvivorsPop

		fitSurvivorsProf = self.currProfiles[self.numFitSurvivors:]
		self.currProfiles = fitSurvivorsProf + fitSurvivorsProf

		for c in range(self.numberOfConfigChoices):
			self.currPopulation[c]["fitness"] = 0.0
			self.currProfiles[c]["fitness"] = 0.0

		# calc Genotype->Phenotype of best config(coalition) and return
		bestGroups = [[] for i in range(maxNumGroups)]
		bestConfigProfiles = [0 for i in range(maxNumGroups)]

		bestConfigGenotype = self.currPopulation[-1]["config"]
		bestProfilesGenotype = self.currProfiles[-1]["config"]

		for gene in bestConfigGenotype:
			bestGroups[gene[1]].append(gene[0])
			bestConfigProfiles[gene[1]] = bestProfilesGenotype[gene[1]]

		while(True):
			if [] in bestGroups:  bestGroups.remove([])
			elif 0 in bestConfigProfiles: bestConfigProfiles.remove(0)
			else: break

		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": [PlayerCharacteristics() for i in range(maxNumGroups)]}
