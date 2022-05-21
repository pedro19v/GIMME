import random
import math
import copy
import numpy
from abc import ABC, abstractmethod

from GIMMECore.ElementOfMultiset import ElementOfMultiset

from GIMMECore.IntegerPartition import IntegerPartition
from GIMMECore.IntegerPartitionGraph import IntegerPartitionGraph
from GIMMECore.Node import Node
from GIMMECore.Subspace import Subspace
from GIMMECore.SubstsOfMultiset import SubsetsOfMultiset

import GIMMESolver as gs
from ctypes import *

from ..InteractionsProfile import InteractionsProfile 
from ..PlayerStructs import *
from ..AlgDefStructs.RegressionAlg import *
import matplotlib.pyplot as plt


class ConfigsGenAlg(ABC):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None):

		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}
		
		minNumberOfPlayersPerGroup = 2 if minNumberOfPlayersPerGroup == None else minNumberOfPlayersPerGroup 
		maxNumberOfPlayersPerGroup = 5 if maxNumberOfPlayersPerGroup == None else maxNumberOfPlayersPerGroup

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


		self.completionPerc = 0.0


	def init(self):
		self.groupSizeFreqs = {}
		self.configSizeFreqs = {}
		return self

	def reset(self):
		return self.init()

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
		if (playersWithoutGroupSize < (math.ceil(self.maxNumberOfPlayersPerGroup) / 2.0)):
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
		else:
			returnedConfig.append(playersWithoutGroup)

		return returnedConfig



	@abstractmethod
	def organize(self):
		pass

	def updateMetrics(self, groups):

		# kind of sub-optimal, but guarantees encapsulation
		if(self.configSizeFreqs.get(len(groups))):
			self.configSizeFreqs[len(groups)]+=1
		else:
			self.configSizeFreqs[len(groups)]=1

		for group in groups:
			if(self.configSizeFreqs.get(len(group))):
				self.configSizeFreqs[len(group)]+=1
			else:
				self.configSizeFreqs[len(group)]=1


	def getCompPercentage(self):
		return self.completionPerc



class RandomConfigsGen(ConfigsGenAlg):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None):
		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

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


			profile = self.interactionsProfileTemplate.generateCopy().randomize()			
			# generate random profile
			# for currPlayer in group:
			# 	random = self.interactionsProfileTemplate.generateCopy().randomize()
			# 	for dim in profile.dimensions:
			# 		profile.dimensions[dim] += random.dimensions[dim] / groupSize
			# profile.normalize()
			newConfigProfiles.append(profile)


			currAvgCharacteristics = PlayerCharacteristics().reset()
			for currPlayer in group:
				currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
				currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
				currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
			# currAvgCharacteristics.profile = profile
			newAvgCharacteristics.append(currAvgCharacteristics)

			self.completionPerc = groupI/newConfigSize

		self.updateMetrics(newGroups)
		return {"groups": newGroups, "profiles": newConfigProfiles, "avgCharacteristics": newAvgCharacteristics}




class AnnealedPRSConfigsGen(ConfigsGenAlg):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg, 
		persEstAlg, 
		temperatureDecay, 
		numberOfConfigChoices = None, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None, 
		qualityWeights = None):

		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.persEstAlg = persEstAlg
		self.numberOfConfigChoices = 100 if numberOfConfigChoices == None else numberOfConfigChoices
		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights 

		self.temperature = 1.0
		self.temperatureDecay = temperatureDecay

	def init(self):
		super().init()
		self.temperature = 1.0

	def reset(self, temperature):
		super().reset()
		self.temperature = numpy.clip(temperature, 0, 1)


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


		# estimate preferences
		self.persEstAlg.updateEstimates()

		# generate several random groups, calculate their fitness and select the best one
		for i in range(self.numberOfConfigChoices):
			
			# generate several random groups
			newGroups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
			newConfigSize = len(newGroups)
			currQuality = 0.0
			newConfigProfiles = []
			newAvgCharacteristics = []

			# generate profiles
			for groupI in range(newConfigSize):
				group = newGroups[groupI]
				groupSize = len(group)

				# generate group profile as random or average of the preferences estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()

				if(random.uniform(0.0, 1.0) > self.temperature):
					for currPlayer in group:
						preferences = self.playerModelBridge.getPlayerPreferencesEst(currPlayer)
						for dim in profile.dimensions:
							profile.dimensions[dim] += preferences.dimensions[dim] / groupSize
					# profile.normalize()
				else:
					profile = self.interactionsProfileTemplate.generateCopy().randomize()

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


			self.completionPerc = i/self.numberOfConfigChoices

		if(self.temperature > 0.0):
			self.temperature -= self.temperatureDecay
		else:
			self.temperature = 1.0

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}




class PureRandomSearchConfigsGen(ConfigsGenAlg):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg, 
		persEstAlg, 
		numberOfConfigChoices = None, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None, 
		qualityWeights = None):
		
		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.persEstAlg = persEstAlg
		self.numberOfConfigChoices = 100 if numberOfConfigChoices == None else numberOfConfigChoices
		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights 

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


		# estimate preferences
		self.persEstAlg.updateEstimates()

		# generate several random groups, calculate their fitness and select the best one
		for i in range(self.numberOfConfigChoices):
			
			# generate several random groups
			newGroups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
			newConfigSize = len(newGroups)
			currQuality = 0.0
			newConfigProfiles = []
			newAvgCharacteristics = []

			# generate profiles
			for groupI in range(newConfigSize):
				group = newGroups[groupI]
				groupSize = len(group)

				# generate profile as average of the preferences estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()

				for currPlayer in group:
					preferences = self.playerModelBridge.getPlayerPreferencesEst(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += (preferences.dimensions[dim] / groupSize)

				# print("profile in-configGen: "+str(profile.dimensions)+";groupSize: "+str(groupSize))
				# profile.normalize()
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


			self.completionPerc = i/self.numberOfConfigChoices

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}




class AccuratePRSConfigsGen(ConfigsGenAlg):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		simulationFunc, 
		numberOfConfigChoices = None, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None, 
		qualityWeights = None):

		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		self.simulationFunc = simulationFunc
		self.currIteration = 0

		self.numberOfConfigChoices = 100 if numberOfConfigChoices == None else numberOfConfigChoices 
		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights

	def init(self):
		super().init()
		self.currIteration = 0

	def updateCurrIteration(self, newCurrIteration):
		self.currIteration = newCurrIteration

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

		# generate several random groups, calculate their fitness and select the best one
		for i in range(self.numberOfConfigChoices):
			
			# generate several random groups
			newGroups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
			newConfigSize = len(newGroups)
			currQuality = 0.0
			newConfigProfiles = []
			newAvgCharacteristics = []

			# generate profiles
			for groupI in range(newConfigSize):
				group = newGroups[groupI]
				groupSize = len(group)

				# generate profile as average of the preferences estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()
				for currPlayer in group:
					preferences = self.playerModelBridge.getPlayerRealPreferences(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += preferences.dimensions[dim] / groupSize
				# profile.normalize()
				newConfigProfiles.append(profile)


				# calculate fitness and average state
				currAvgCharacteristics = PlayerCharacteristics()
				currAvgCharacteristics.reset()
				for currPlayer in group:

					currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
					currState.profile = profile

					currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
					currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
				
					# does not matter if its executed as bootstrap or not
					newState = self.simulationFunc(
						isBootstrap = False, 
						playerBridge = self.playerModelBridge, 
						state = currState, 
						playerId = currPlayer, 
						currIteration = self.currIteration)
					increases = PlayerState()
					increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
					currQuality += self.calcQuality(increases)

				newAvgCharacteristics.append(currAvgCharacteristics)
			
			if (currQuality > currMaxQuality):
				bestGroups = newGroups
				bestConfigProfiles = newConfigProfiles
				bestAvgCharacteristics = newAvgCharacteristics
				currMaxQuality = currQuality

			self.completionPerc = i/self.numberOfConfigChoices


		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}



from deap import base, creator, tools, algorithms
from collections import *

class EvolutionaryConfigsGenDEAP(ConfigsGenAlg):
	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg = None, 
		numberOfConfigChoices = 0,
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None, 
		qualityWeights = None,

		initialPopulationSize = None, 
		numberOfEvolutionsPerIteration = None,  
		probOfCross = None, 

		probOfMutation = None,
		probOfMutationConfig = None, 
		probOfMutationGIPs = None, 

		numChildrenPerIteration = None,
		numSurvivors = None,

		cxOp = None):

		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.initialPopulationSize = 100 if initialPopulationSize == None else initialPopulationSize 


		self.numberOfEvolutionsPerIteration = 500 if numberOfEvolutionsPerIteration == None else numberOfEvolutionsPerIteration
		
		self.probOfMutation = 0.2 if probOfMutation == None else probOfMutation
		self.probOfCross = 0.7 if probOfCross == None else probOfCross
		
		self.probOfMutationConfig = 0.2 if probOfMutationConfig == None else probOfMutationConfig
		self.probOfMutationGIPs = 0.2 if probOfMutationGIPs == None else probOfMutationGIPs
		

		self.numChildrenPerIteration = 5 if numChildrenPerIteration == None else numChildrenPerIteration 
		self.numSurvivors = 5 if numSurvivors == None else numSurvivors 

		if(regAlg==None):
			regAlg = KNNRegression(playerModelBridge, 5)

		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights

		self.playerIds = self.playerModelBridge.getAllPlayerIds() 
		self.minNumGroups = math.ceil(len(self.playerIds) / self.maxNumberOfPlayersPerGroup)
		self.maxNumGroups = math.floor(len(self.playerIds) / self.minNumberOfPlayersPerGroup)

		self.searchID = str(id(self)) 

		fitnessFuncId = "FitnessMax"+self.searchID
		individualId = "Individual"+self.searchID

		creator.create(fitnessFuncId, base.Fitness, weights=(1.0,))
		creator.create(individualId, list, fitness=getattr(creator, fitnessFuncId))

		# # conv test
		# creator.create(fitnessFuncId, base.Fitness, weights=(-1.0,))
		# creator.create(individualId, list, fitness=getattr(creator, fitnessFuncId))

		
		self.toolbox = base.Toolbox()

		self.toolbox.register("indices", self.randomIndividualGenerator, self.playerIds, self.minNumGroups, self.maxNumGroups)

		self.toolbox.register("individual", tools.initIterate, getattr(creator, individualId), self.toolbox.indices)
		self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

		self.cxOp = "order" if cxOp == None else cxOp
		if self.cxOp == "order":
			self.toolbox.register("mate", self.cxGIMME_Order)
		else:
			self.toolbox.register("mate", self.cxGIMME_Simple)

		self.toolbox.register("mutate", self.mutGIMME, pGIPs=self.probOfMutationGIPs, pConfig=self.probOfMutationConfig)

		# self.toolbox.register("select", tools.selRoulette)
		# self.toolbox.register("select", tools.selBest, k=self.numFitSurvivors)
		self.toolbox.register("select", tools.selBest)

		# self.toolbox.register("evaluate", self.calcFitness_convergenceTest)
		self.toolbox.register("evaluate", self.calcFitness)

		self.resetGenAlg()


	def resetGenAlg(self):

		if hasattr(self, "pop"):
			del self.pop
		if hasattr(self, "hof"):
			del self.hof

		self.pop = self.toolbox.population(n = self.initialPopulationSize)
		self.hof = tools.HallOfFame(1)



	def randomIndividualGenerator(self, playerIds, minNumGroups, maxNumGroups):
		groups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
		profs = [self.randomProfileGenerator() for i in range(len(groups))]
		return [groups, profs]

	def randomProfileGenerator(self):
		return self.interactionsProfileTemplate.randomized()


	def cxGIMME_Order(self, ind1, ind2):

		# configs
		config1 = ind1[0]
		config2 = ind2[0]

		newConfig1 = []
		newConfig2 = []

		l1 = len(config1)
		l2 = len(config2)

		if (l1 > l2):
			maxLenConfig = config1
			maxLen = l1
			minLenConfig = config2
			minLen = l2
		else:
			maxLenConfig = config2
			maxLen = l2
			minLenConfig = config1
			minLen = l1

		cxpoints = [] 
		
		clist1 = []
		clist2 = []

		remainder1 = []
		remainder2 = []
		for i in range(minLen):
			parent1 = minLenConfig[i]
			parent2 = maxLenConfig[i]

			cxpoint = random.randint(0,len(minLenConfig[i]))
			cxpoints.append(cxpoint) 

			clist1.extend(parent1)
			clist2.extend(parent2)

			remainder1.extend(parent1[cxpoint:])
			remainder2.extend(parent2[cxpoint:])


		d1 = {k:v for v,k in enumerate(clist1)}
		d2 = {k:v for v,k in enumerate(clist2)}

		remainder1.sort(key=d2.get)
		remainder2.sort(key=d1.get)

		for i in range(minLen):
			parent1 = minLenConfig[i]
			parent2 = maxLenConfig[i]

			cxpoint = cxpoints[i] 

			#C1 Implementation
			# maintain left part
			child1, child2 = parent1[:cxpoint], parent2[:cxpoint]


			# reorder right part
			missingLen1 = len(parent1) - len(child1)
			child1.extend(remainder1[:missingLen1])
			remainder1 = remainder1[missingLen1:]

			missingLen2 = len(parent2) - len(child2)
			child2.extend(remainder2[:missingLen2])
			remainder2 = remainder2[missingLen2:]

			newConfig1.append(child1)
			newConfig2.append(child2)


		#the inds become children
		ind1[0] = newConfig1
		ind2[0] = newConfig2

		# breakpoint()

		# profiles are crossed with one point (no need for that when profiles are 1D)
		# breakpoint()
		# if self.interactionsProfileTemplate.dimensionality > 1:
		for i in range(minLen):
			prof1 = ind1[1][i].flattened()
			prof2 = ind2[1][i].flattened()

			newProfiles = tools.cxUniform(prof1, prof2, 0.5)
			# newProfiles = tools.cxOnePoint(prof1, prof2)
			
			#the inds become children
			ind1[1][i] = self.interactionsProfileTemplate.unflattened(newProfiles[0])
			ind2[1][i] = self.interactionsProfileTemplate.unflattened(newProfiles[1])

			# breakpoint()

		del ind1.fitness.values
		del ind2.fitness.values

		return (ind1, ind2)


	def cxGIMME_Simple(self, ind1, ind2):

		# configs
		config1 = ind1[0]
		config2 = ind2[0]

		newConfig1 = []
		newConfig2 = []

		l1 = len(config1)
		l2 = len(config2)

		if (l1 > l2):
			maxLenConfig = config1
			maxLen = l1
			minLenConfig = config2
			minLen = l2
		else:
			maxLenConfig = config2
			maxLen = l2
			minLenConfig = config1
			minLen = l1

		cxpoints = [] 
		
		clist1 = []
		clist2 = []

		remainder1 = []
		remainder2 = []
		for i in range(minLen):
		
			parent1 = [None, None]
			parent2 = [None, None]

			parent1[0] = minLenConfig[i]
			parent1[1] = ind1[1][i].flattened()
			parent2[0] = maxLenConfig[i]
			parent2[1] = ind2[1][i].flattened()

			clist1.append(parent1)
			clist2.append(parent2)


		# breakpoint()

		for ind,clist in zip([ind1,ind2], [clist1,clist2]):


			# print("-----------[Before]-----------")
			# print(json.dumps(ind[1], default=lambda o: o.__dict__))

			randI1 = random.randint(0, len(clist1) - 1)
			randI2 = random.randint(0, len(clist1) - 1)
			

			newProfilesConfig = tools.cxOnePoint(ind1 = clist[randI1][0], ind2 = clist[randI2][0])
			newProfilesGIP = tools.cxOnePoint(ind1 = clist[randI1][1], ind2 = clist[randI2][1])
			
			ind[0][randI1] = newProfilesConfig[0]
			ind[1][randI1] = self.interactionsProfileTemplate.unflattened(newProfilesGIP[0])

			ind[0][randI2] = newProfilesConfig[1]
			ind[1][randI2] = self.interactionsProfileTemplate.unflattened(newProfilesGIP[1])

			# print("-----------[After]-----------")
			# print(json.dumps(ind[1], default=lambda o: o.__dict__))

		# breakpoint()



		del ind1.fitness.values
		del ind2.fitness.values

		return (ind1, ind2)


	def mutGIMME(self, individual, pGIPs, pConfig):
		
		# mutate config
		if random.uniform(0, 1) <= pConfig:
			
			numberOfMutations = 1
			for i in range(numberOfMutations):
				# breakpoint()
				indCpy = copy.copy(individual)
				
				randI1 = random.randint(0, len(indCpy[0]) - 1)
				innerRandI1 = random.randint(0, len(indCpy[0][randI1]) - 1)

				randI2 = innerRandI2 = -1
				while(randI2 < 0 or randI1 == randI2):
					randI2 = random.randint(0, len(indCpy[0]) - 1)
				while(innerRandI2 < 0 or innerRandI1 == innerRandI2):
					innerRandI2 = random.randint(0, len(indCpy[0][randI2]) - 1)


				elem1 = indCpy[0][randI1][innerRandI1]
				elem2 = indCpy[0][randI2][innerRandI2]


				indCpy[0][randI1][innerRandI1] = elem2
				indCpy[0][randI2][innerRandI2] = elem1

				individual[0] = indCpy[0]
				# breakpoint()
			

		#mutate GIPs
		numberOfMutations = 1
		for i in range(numberOfMutations):
			profs = individual[1]
			keys = list(profs[0].dimensions.keys())
			for i in range(len(profs)):
				if random.uniform(0, 1) <= pGIPs:
					# profs[i].randomize()
					for key in keys:
						if random.uniform(0, 1) <= 0.5:
							profs[i].dimensions[key] += random.uniform(0, min(0.2, 1.0 - profs[i].dimensions[key])) 
						else:
							profs[i].dimensions[key] -= random.uniform(0, min(0.2, profs[i].dimensions[key])) 

			individual[1] = profs
		
		del individual.fitness.values
		return individual,


	def reset(self):
		super().reset()
		self.resetGenAlg()

	def calcFitness_convergenceTest(self, individual):
		config = individual[0]
		profiles = individual[1]

		totalFitness = 0.0

		targetConfig = [[0,1,2,3], [4,5,6,7], [8,9,10,11], [12,13,14,15], [16,17,18,19], [20,21,22,23]]

		lenConfig = len(config)
		for groupI in range(lenConfig):
			
			group = config[groupI]
			profile = profiles[groupI]
			
			for playerI in range(len(group)):
				totalFitness += profile.sqrDistanceBetween(InteractionsProfile(dimensions = {'dim_0': 0.98, 'dim_1': 0.005}))
				totalFitness += abs(config[groupI][playerI] - targetConfig[groupI][playerI])
		
		print(totalFitness)
		totalFitness = totalFitness + 1.0 #helps selection (otherwise Pchoice would always be 0)
		individual.fitness.values = totalFitness,
		return totalFitness, #must return a tuple



	def calcFitness(self, individual):
		config = individual[0]
		profiles = individual[1]

		totalFitness = 0.0

		lenConfig = len(config)
		for groupI in range(lenConfig):
			
			group = config[groupI]
			profile = profiles[groupI]

			# breakpoint()
			for playerId in group:
				predictedIncreases = self.regAlg.predict(profile, playerId)
				totalFitness += (self.qualityWeights.ability* predictedIncreases.characteristics.ability + \
								self.qualityWeights.engagement* predictedIncreases.characteristics.engagement)
		
		totalFitness = totalFitness + 1.0 #helps selection (otherwise Pchoice would always be 0)
		individual.fitness.values = totalFitness,

		return totalFitness, #must return a tuple



	def organize(self):
		self.resetGenAlg()
		algorithms.eaMuCommaLambda(
			population = self.pop, 
			toolbox = self.toolbox, 

			lambda_ = self.numChildrenPerIteration, 
			mu = self.numSurvivors, 
			
			cxpb = self.probOfCross, 
			mutpb = self.probOfMutation, 
			
			ngen = self.numberOfEvolutionsPerIteration, 
			
			halloffame = self.hof, 
			verbose = False
		)


		self.completionPerc = len(tools.Logbook())/ self.numberOfEvolutionsPerIteration

		bestGroups = self.hof[0][0]
		bestConfigProfiles = self.hof[0][1]

		# print(bestGroups)
		# print(bestConfigProfiles[0].dimensions)
		# breakpoint()

		avgCharacteristicsArray = []
		for group in bestGroups:
			groupSize = len(group)
			avgCharacteristics = PlayerCharacteristics()
			for currPlayer in group:
				currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
				avgCharacteristics.ability += currState.characteristics.ability / groupSize
				avgCharacteristics.engagement += currState.characteristics.engagement / groupSize
			avgCharacteristicsArray.append(avgCharacteristics)

		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": avgCharacteristicsArray}

# new algorithms
class ODPIP(ConfigsGenAlg):
	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg,
		persEstAlg,
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None,
		qualityWeights = None):

		super().__init__(playerModelBridge, 
		interactionsProfileTemplate, 
		preferredNumberOfPlayersPerGroup, 
		minNumberOfPlayersPerGroup, 
		maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.persEstAlg = persEstAlg

		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights 

		self.coalitionsProfiles = []
		self.coalitionsAvgCharacteristics = []
		self.coalitionsValues = []

		self.playerIds = []	

	def calcQuality(self, state):
		return self.qualityWeights.ability*state.characteristics.ability + self.qualityWeights.engagement*state.characteristics.engagement

	def getCoalitionInByteFormatValue(self, coalitionInByteFormat):
		coalitionInBitFormat = self.convertCoalitionFromByteToBitFormat(coalitionInByteFormat, len(coalitionInByteFormat))
		return self.f[coalitionInBitFormat]


	def getCoalitionStructureInByteFormatValue(self, coalitionStructure):
		valueOfCS = 0
		for i in range(len(coalitionStructure)):
			valueOfCS += self.getCoalitionInByteFormatValue(coalitionStructure[i])
		
		return valueOfCS


	def convertCoalitionFromByteToBitFormat(self, coalitionInByteFormat, coalitionSize):
		coalitionInBitFormat = 0

		for i in range(coalitionSize):
			coalitionInBitFormat += 1 << (coalitionInByteFormat[i] - 1)

		return coalitionInBitFormat

	# convert group in bit format to group with the player ids
	def getGroupFromBitFormat(self, coalition):
		group = []
		tempCoalition = coalition
		playerNumber = 0
		while tempCoalition != 0:
			if tempCoalition & 1:
				group.append(playerNumber + 1)

			playerNumber += 1
			tempCoalition >>= 1

		
		return group

	def convertFromByteToIds(self, coalition):
		group = []

		for agent in coalition:
			group.append(self.playerIds[agent - 1])

		return group

	def getSizeOfCombinationInBitFormat(self, combinationInBitFormat):
		return bin(combinationInBitFormat).count("1")


	def convertSetOfCombinationsFromBitFormat(self, setOfCombinationsInBitFormat):
		setOfCombinationsInByteFormat = numpy.empty(len(setOfCombinationsInBitFormat), dtype=list)
		for i in range(len(setOfCombinationsInBitFormat)):

			setOfCombinationsInByteFormat[i] = self.getGroupFromBitFormat(setOfCombinationsInBitFormat[i])

		return setOfCombinationsInByteFormat

	def computeAllCoalitionsValues(self):
		numOfAgents = len(self.playerIds)
		numOfCoalitions = 1 << (numOfAgents)

		# initialize all coalitions
		for coalition in range(numOfCoalitions-1, 0, -1):
			group = self.getGroupFromBitFormat(coalition)
			groupInIds = self.convertFromByteToIds(group)

			currQuality = 0.0
			groupSize = len(group)

			# calculate the profile and characteristics only for groups in the range defined
			if groupSize >= self.minNumberOfPlayersPerGroup and groupSize <= self.maxNumberOfPlayersPerGroup + 1:	
				# generate profile as average of the preferences estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()

				for currPlayer in groupInIds:
					preferences = self.playerModelBridge.getPlayerPreferencesEst(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += (preferences.dimensions[dim] / groupSize)

				# calculate fitness and average state
				currAvgCharacteristics = PlayerCharacteristics()
				currAvgCharacteristics.reset()
				for currPlayer in groupInIds:

					currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
					currState.profile = profile

					currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
					currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
				
					predictedIncreases = self.regAlg.predict(profile, currPlayer)
					currQuality += self.calcQuality(predictedIncreases)

				self.coalitionsAvgCharacteristics[coalition] = currAvgCharacteristics
				self.coalitionsProfiles[coalition] = profile
			
			self.coalitionsValues[coalition] = currQuality


	def results(self, cSInByteFormat):
		bestGroups = []
		bestGroupsInBitFormat = []
		bestConfigProfiles = []
		avgCharacteristicsArray = []
		for coalition in cSInByteFormat:
			bestGroups.append(self.convertFromByteToIds(coalition))
			bestGroupsInBitFormat.append(self.convertCoalitionFromByteToBitFormat(coalition, len(coalition)))

		for group in bestGroupsInBitFormat:
			bestConfigProfiles.append(self.coalitionsProfiles[group])
			avgCharacteristicsArray.append(self.coalitionsAvgCharacteristics[group])

		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": avgCharacteristicsArray}

	def organize(self):
		self.playerIds = sorted(self.playerModelBridge.getAllPlayerIds())
		self.numPlayers = len(self.playerIds)

		self.coalitionsProfiles = numpy.empty(1 << self.numPlayers, dtype=InteractionsProfile)
		self.coalitionsAvgCharacteristics = numpy.empty(1 << self.numPlayers, dtype=PlayerCharacteristics)
		self.coalitionsValues = numpy.empty(1 << self.numPlayers)

		# estimate preferences
		self.persEstAlg.updateEstimates()

		# initialization(compute the value for every coalition between min and max number of players)
		self.computeAllCoalitionsValues()

		bestCSFound_bitFormat = (gs.odpip(self.numPlayers, self.minNumberOfPlayersPerGroup, self.maxNumberOfPlayersPerGroup, self.coalitionsValues.tolist()))
		bestCSFound_byteFormat = self.convertSetOfCombinationsFromBitFormat(bestCSFound_bitFormat)
		return self.results(bestCSFound_byteFormat)


class CLink(ConfigsGenAlg):
	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg,
		persEstAlg,
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None,
		qualityWeights = None):

		super().__init__(playerModelBridge, 
		interactionsProfileTemplate, 
		preferredNumberOfPlayersPerGroup, 
		minNumberOfPlayersPerGroup, 
		maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.persEstAlg = persEstAlg

		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights 

		self.coalitionsProfiles = []
		self.coalitionsAvgCharacteristics = []
		self.coalitionsValues = []

		self.playerIds = []	

	def calcQuality(self, state):
		return self.qualityWeights.ability*state.characteristics.ability + self.qualityWeights.engagement*state.characteristics.engagement

	def getCoalitionInByteFormatValue(self, coalitionInByteFormat):
		coalitionInBitFormat = self.convertCoalitionFromByteToBitFormat(coalitionInByteFormat, len(coalitionInByteFormat))
		return self.f[coalitionInBitFormat]


	def getCoalitionStructureInByteFormatValue(self, coalitionStructure):
		valueOfCS = 0
		for i in range(len(coalitionStructure)):
			valueOfCS += self.getCoalitionInByteFormatValue(coalitionStructure[i])
		
		return valueOfCS


	def convertCoalitionFromByteToBitFormat(self, coalitionInByteFormat, coalitionSize):
		coalitionInBitFormat = 0

		for i in range(coalitionSize):
			coalitionInBitFormat += 1 << (coalitionInByteFormat[i] - 1)

		return coalitionInBitFormat

	# convert group in bit format to group with the player ids
	def getGroupFromBitFormat(self, coalition):
		group = []
		tempCoalition = coalition
		playerNumber = 0
		while tempCoalition != 0:
			if tempCoalition & 1:
				group.append(playerNumber + 1)

			playerNumber += 1
			tempCoalition >>= 1

		
		return group

	def convertFromByteToIds(self, coalition):
		group = []

		for agent in coalition:
			group.append(self.playerIds[agent - 1])

		return group

	def getSizeOfCombinationInBitFormat(self, combinationInBitFormat):
		return bin(combinationInBitFormat).count("1")


	def convertSetOfCombinationsFromBitFormat(self, setOfCombinationsInBitFormat):
		setOfCombinationsInByteFormat = numpy.empty(len(setOfCombinationsInBitFormat), dtype=list)
		for i in range(len(setOfCombinationsInBitFormat)):

			setOfCombinationsInByteFormat[i] = self.getGroupFromBitFormat(setOfCombinationsInBitFormat[i])

		return setOfCombinationsInByteFormat

	def computeAllCoalitionsValues(self):
		numOfAgents = len(self.playerIds)
		numOfCoalitions = 1 << (numOfAgents)

		# initialize all coalitions
		for coalition in range(numOfCoalitions-1, 0, -1):
			group = self.getGroupFromBitFormat(coalition)
			groupInIds = self.convertFromByteToIds(group)

			currQuality = 0.0
			groupSize = len(group)

			# calculate the profile and characteristics only for groups in the range defined
			if groupSize <= self.maxNumberOfPlayersPerGroup + 1:	
				# generate profile as average of the preferences estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()

				for currPlayer in groupInIds:
					preferences = self.playerModelBridge.getPlayerPreferencesEst(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += (preferences.dimensions[dim] / groupSize)

				# calculate fitness and average state
				currAvgCharacteristics = PlayerCharacteristics()
				currAvgCharacteristics.reset()
				for currPlayer in groupInIds:

					currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
					currState.profile = profile

					currAvgCharacteristics.ability += currState.characteristics.ability / groupSize
					currAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
				
					predictedIncreases = self.regAlg.predict(profile, currPlayer)
					currQuality += self.calcQuality(predictedIncreases)

				self.coalitionsAvgCharacteristics[coalition] = currAvgCharacteristics
				self.coalitionsProfiles[coalition] = profile
			
			self.coalitionsValues[coalition] = currQuality


	def results(self, cSInByteFormat):
		bestGroups = []
		bestGroupsInBitFormat = []
		bestConfigProfiles = []
		avgCharacteristicsArray = []
		for coalition in cSInByteFormat:
			bestGroups.append(self.convertFromByteToIds(coalition))
			bestGroupsInBitFormat.append(self.convertCoalitionFromByteToBitFormat(coalition, len(coalition)))

		for group in bestGroupsInBitFormat:
			bestConfigProfiles.append(self.coalitionsProfiles[group])
			avgCharacteristicsArray.append(self.coalitionsAvgCharacteristics[group])

		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": avgCharacteristicsArray}

	def organize(self):
		self.playerIds = sorted(self.playerModelBridge.getAllPlayerIds())
		self.numPlayers = len(self.playerIds)

		self.coalitionsProfiles = numpy.empty(1 << self.numPlayers, dtype=InteractionsProfile)
		self.coalitionsAvgCharacteristics = numpy.empty(1 << self.numPlayers, dtype=PlayerCharacteristics)
		self.coalitionsValues = numpy.empty(1 << self.numPlayers)

		# estimate preferences
		self.persEstAlg.updateEstimates()

		# initialization(compute the value for every coalition between min and max number of players)
		self.computeAllCoalitionsValues()

		bestCSFound_bitFormat = (gs.clink(self.numPlayers, self.minNumberOfPlayersPerGroup, self.maxNumberOfPlayersPerGroup, self.coalitionsValues.tolist()))
		bestCSFound_byteFormat = self.convertSetOfCombinationsFromBitFormat(bestCSFound_bitFormat)
		return self.results(bestCSFound_byteFormat)
