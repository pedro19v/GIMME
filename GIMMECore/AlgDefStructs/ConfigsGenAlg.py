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

		# IP variables
		self.ipNumOfExpansions = 0
		self.ipValueOfBestCSFound = -1
		self.ipBestCSFound = None
		self.totalNumOfExapnsions = 0
		self.ipIntegerPartitionGraph = None
		self.ipUpperBoundOnOptimalValue = 0
		self.ipLowerBoundOnOptimalValue = 0

		# DP variables
		self.dpValueOfBestCSFound = -1
		self.dpBestCSFound = None
		self.odpMaxSizeComputedSoFar = 0
		self.odpHasFinished = False

		self.feasibleCoalitions = []

		self.coalitionsProfiles = []
		self.coalitionsAvgCharacteristics = []
		self.coalitionsValues = []
		self.f = []
		self.maxF = []

		self.playerIds = []
		self.pascalMatrix = []

		self.tooManyPlayers = False

	

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


	def copyMultiset(multiset):
		if multiset == None:
			return None

		copy = numpy.empty(len(multiset))
		for i in range(len(multiset)):
			copy[i] = ElementOfMultiset(multiset[i].element, multiset[i].repetition)

		return copy

	
	def getCardinalityOfMultiset(multiset):
		if multiset == None:
			return 0

		counter = 0
		for i in range(len(multiset)):
			counter += multiset[i].repetition

		return counter

	#IP functions
	def updateIPSolution(self, CS, value):
		if self.ipValueOfBestCSFound <= value:
			self.ipValueOfBestCSFound = value
			self.ipBestCSFound = CS[:]

	def updateNumOfSearchedAndRemainingCoalitionsAndCoalitionStructures(self):
		for size1 in range(1, math.floor(self.numPlayers/2)+1):
			size2 = self.numPlayers - size1

			numOfCombinationsOfSize1 = int(math.comb(self.numPlayers, size1))

			temp = 0
			if size1 != size2:
				temp = numOfCombinationsOfSize1
			else:
				temp = int(numOfCombinationsOfSize1/2)

			self.ipNumOfExpansions += 2*temp

	def searchFirstAndLastLevel(self):
		CS1IsFeasible = True
		CS2IsFeasible = True

		CS1 = numpy.empty((self.numPlayers, 1), dtype=int)
		for i in range(self.numPlayers):
			CS1[i][0] = i + 1

		CS2 = numpy.empty((1, self.numPlayers), dtype=int)
		for i in range(self.numPlayers):
			CS2[0][i] = i + 1

		if self.feasibleCoalitions != []:
			for i in range(len(CS1)):
				curCoalitionInBitFormat = self.convertCoalitionFromByteToBitFormat(CS1[i])
				if curCoalitionInBitFormat not in self.feasibleCoalitions:
					CS1IsFeasible = False
					break
			
			for i in range(len(CS2)):
				curCoalitionInBitFormat = self.convertCoalitionFromByteToBitFormat(CS2[i])
				if curCoalitionInBitFormat not in self.feasibleCoalitions:
					CS2IsFeasible = False
					break
		
		valueOfCS1 = self.getCoalitionStructureInByteFormatValue(CS1)
		valueOfCS2 = self.getCoalitionStructureInByteFormatValue(CS2)

		if ((CS1IsFeasible) and (CS2IsFeasible == False)) or (CS1IsFeasible and CS2IsFeasible and valueOfCS1 >= valueOfCS2):
			self.updateIPSolution(CS1, valueOfCS1)

		if ((CS2IsFeasible) and (CS1IsFeasible == False)) or (CS2IsFeasible and CS1IsFeasible and valueOfCS2 >= valueOfCS1):
			self.updateIPSolution(CS2, valueOfCS2)

	def computeAvgForEachSize(self):
		totalNumOfCoalitions = 2 ** self.numPlayers
		bestValue = self.ipValueOfBestCSFound
		bestCoalition1 = 0
		bestCoalition2 = 0
		sumOfValues = numpy.zeros(self.numPlayers)

		coalition1IsFeasible = True
		coalition2IsFeasible = True
		constraintsExist = False

		if self.feasibleCoalitions != []:
			constraintsExist = True

		for coalition1 in range((int)(totalNumOfCoalitions/2), totalNumOfCoalitions-1):
			sizeOfCoalition1 = self.getSizeOfCombinationInBitFormat(coalition1)

			coalition2 = totalNumOfCoalitions - 1 - coalition1
			sizeOfCoalition2 = self.numPlayers - sizeOfCoalition1

			sumOfValues[sizeOfCoalition1 - 1] += self.f[coalition1]
			sumOfValues[sizeOfCoalition2 - 1] += self.f[coalition2]

			if constraintsExist:
				coalition1IsFeasible = coalition1 in self.feasibleCoalitions
				coalition2IsFeasible = coalition2 in self.feasibleCoalitions

			value = 0
			if (constraintsExist == False) or (coalition1IsFeasible and coalition2IsFeasible):
				value = self.f[coalition1] + self.f[coalition2]

			if bestValue < value:
				bestCoalition1 = coalition1
				bestCoalition2 = coalition2
				bestValue = value

		if bestValue > self.ipValueOfBestCSFound:
			bestCS = numpy.empty(2, dtype=list)
			bestCS[0] = self.getGroupFromBitFormat(bestCoalition1)
			bestCS[1] = self.getGroupFromBitFormat(bestCoalition2)
			self.updateIPSolution(bestCS, bestValue)

		avgValueForEachSize = numpy.zeros(self.numPlayers)
		for size in range(1, self.numPlayers + 1):
			avgValueForEachSize[size-1] = (sumOfValues[size-1] / math.comb(self.numPlayers, size))

		self.updateNumOfSearchedAndRemainingCoalitionsAndCoalitionStructures()

		return avgValueForEachSize

	def setMaxValueForEachSize(self):
		numOfRequiredMaxValues = numpy.empty(self.numPlayers, dtype=int)
		numOfCoalitions = numpy.empty(self.numPlayers, dtype=numpy.int64)
		maxValue = numpy.empty(self.numPlayers, dtype=list)

		for size in range(1, self.numPlayers + 1):
			numOfRequiredMaxValues[size-1] = math.floor(self.numPlayers/size)
			numOfCoalitions[size-1] = math.comb(self.numPlayers, size)
			maxValue[size-1] = numpy.zeros(numOfRequiredMaxValues[size-1])

		constraintsExist = False
		if self.feasibleCoalitions != []:
			constraintsExist = True

		for coalitionInBitFormat in range((2**self.numPlayers) - 1, 0, -1):
			if constraintsExist == False or coalitionInBitFormat in self.feasibleCoalitions:
				size = self.getSizeOfCombinationInBitFormat(coalitionInBitFormat)
				curMaxValue = maxValue[size-1]
				j = numOfRequiredMaxValues[size-1]-1
				if self.f[coalitionInBitFormat] > curMaxValue[j]:
					while j > 0 and self.f[coalitionInBitFormat] > curMaxValue[j-1]:
						curMaxValue[j] = curMaxValue[j-1]
						j -= 1
					curMaxValue[j] = self.f[coalitionInBitFormat]

		return maxValue

	def initSubspaces(self, avgValueForEachSize, maxValueForEachSize):
		integers = IntegerPartition.getIntegerPartitions(self.numPlayers)
		
		subspaces = [[] for _ in range(len(integers))]
		for level in range(self.numPlayers):
			subspaces[level] = numpy.empty(len(integers[level]), dtype=Subspace)
		
			for i in range(len(integers[level])):
				subspaces[level][i] = Subspace(integers[level][i], avgValueForEachSize, maxValueForEachSize, self.numPlayers)
		
		return subspaces

	def computeTotalNumOfExpansions(self):
		totalNumOfExpansions = 0
		nodes = self.ipIntegerPartitionGraph.nodes
		for level in range(len(nodes)):
			for i in range(len(nodes[level])):
				curSubspace = nodes[level][i].subspace
				totalNumOfExpansions += curSubspace.totalNumOfExpansionsInSubspace

		return totalNumOfExpansions

	def disableSubspacesThatWereSearchedInTheBeginning(self):
		nodes = self.ipIntegerPartitionGraph.nodes
		numOfSubspacesThatThisMethodHasDisabled = 0
		for level in range(len(nodes)):
			for i in range(len(nodes[level])):
				curSubspace = nodes[level][i].subspace
				if level == 0 or level == 1 or level == self.numPlayers-1:
					if curSubspace.enabled:
						curSubspace.enabled = False
						numOfSubspacesThatThisMethodHasDisabled += 1

		return numOfSubspacesThatThisMethodHasDisabled

	def setUpperAndLowerBoundsOnOptimalValue(self):
		self.ipUpperBoundOnOptimalValue = self.ipValueOfBestCSFound
		self.ipLowerBoundOnOptimalValue = self.ipValueOfBestCSFound

		nodes = self.ipIntegerPartitionGraph.nodes
		for level in range(len(nodes)):
			for i in range(len(nodes[level])):
				curSubspace = nodes[level][i].subspace
				if curSubspace.enabled:
					if self.ipUpperBoundOnOptimalValue < curSubspace.UB:
						self.ipUpperBoundOnOptimalValue = curSubspace.UB

					if self.ipLowerBoundOnOptimalValue < curSubspace.LB:
						self.ipLowerBoundOnOptimalValue = curSubspace.LB


	def disableSubspacesWithUBLowerThanTheHighestLB(self):
		nodes = self.ipIntegerPartitionGraph.nodes

		numOfSubspacesThatThisMethodHasDisabled = 0

		for level in range(len(nodes)):
			for i in range(len(nodes[level])):
				curSubspace = nodes[level][i].subspace
				if curSubspace.enabled:
					if curSubspace.UB - self.ipLowerBoundOnOptimalValue < -0.00000000005:
						curSubspace.enabled = False
						numOfSubspacesThatThisMethodHasDisabled += 1

		return numOfSubspacesThatThisMethodHasDisabled

	def disableSubspacesReachableFromBottomNode(self):
		bottomNode = self.ipIntegerPartitionGraph.nodes[0][0]

		reachableNodes = self.ipIntegerPartitionGraph.getReachableNodes(bottomNode)

		numOfDisabledNodes = 0
		if reachableNodes is not None:
			for i in range(len(reachableNodes)):
				if reachableNodes[i].subspace.enabled:
					reachableNodes[i].subspace.enabled = False
					numOfDisabledNodes += 1
		
		return numOfDisabledNodes

	def getListOfSortedNodes(self, subspaces):
		nodes = self.ipIntegerPartitionGraph.nodes

		for level in range(len(nodes)):
			for i in range(len(nodes[level])):
				curSubspace = nodes[level][i].subspace
				curSubspace.priority = curSubspace.UB

		sortedNodes = numpy.empty(IntegerPartition.getNumOfIntegerPartitions(self.numPlayers), dtype=Node)
		k = 0
		for level in range(len(nodes)):
			for i in range(len(nodes[level])):
				sortedNodes[k] = nodes[level][i]
				k += 1

		for i in range(len(sortedNodes)-1, -1, -1):
			indexOfSmallestElement = i
			for j in range(i, -1, -1):
				if sortedNodes[j].subspace.priority < sortedNodes[indexOfSmallestElement].subspace.priority or \
					(sortedNodes[j].subspace.priority == sortedNodes[indexOfSmallestElement].subspace.priority 
						and sortedNodes[j].subspace.UB < sortedNodes[indexOfSmallestElement].subspace.UB):
					indexOfSmallestElement = j

			temp = sortedNodes[i]
			sortedNodes[i] = sortedNodes[indexOfSmallestElement]
			sortedNodes[indexOfSmallestElement] = temp
		
		return sortedNodes

	def getFirstEnabledNode(self, sortedNodes):
		#breakpoint()
		for i in range(len(sortedNodes)):
			if sortedNodes[i].subspace.enabled:
				return sortedNodes[i]

		return None

	def getRelevantNodes(self, node, numOfIntegersToSplitAtTheEnd):
		numOfIntegersInNode = len(node.integerPartition.partsSortedAscendingly)

		reachableNodes = self.ipIntegerPartitionGraph.getReachableNodes(node)

		if reachableNodes == None:
			node.subspace.relevantNodes = None
			return None

		subsetIterators = numpy.empty(numOfIntegersToSplitAtTheEnd)
		for s in range(numOfIntegersToSplitAtTheEnd):
			subsetIterators[s] = SubsetsOfMultiset(node.integerPartition.sortedMultiset, numOfIntegersInNode - s + 1, False)

		bestSubset = None
		bestSavings = 0
		bestNumOfRelevantNodes = 0

		for s in range(numOfIntegersToSplitAtTheEnd):
			subset = subsetIterators[s].getNextSubset()
			while subset != None:
				savings = 0
				numOfRelevantSubspaces = 0

				for i in range(len(reachableNodes)):
					if reachableNodes[i].integerPartition.contains(subset) and reachableNodes[i].subspace.enabled:
						savings += reachableNodes[i].subspace.totalNumOfExpansionsInSubspace
						numOfRelevantSubspaces += 1

				if bestSavings < savings:
					bestSavings = savings
					bestSubset = ODPIP.copyMultiset(subset)
					bestNumOfRelevantNodes = numOfRelevantSubspaces

				subset = subsetIterators[s].getNextSubset()

		index = 0
		if bestNumOfRelevantNodes == 0:
			node.subspace.relevantNodes = None
			return None

		else:
			node.subspace.relevantNodes = numpy.empty(bestNumOfRelevantNodes)
			for i in range(len(reachableNodes)):
				if reachableNodes[i].integerPartition.contains(bestSubset) and reachableNodes[i].subspace.enabled:
					node.subspace.relevantNodes[index] = reachableNodes[i]
					index += 1

			return bestSubset


	def putSubsetAtTheBeginning(self, node, subset):
		if subset == None:
			return
		
		remainingIntegers_multiset = ODPIP.copyMultiset(node.integerPartition.sortedMultiset)
		for i in range(len(subset)):
			for j in range(len(remainingIntegers_multiset)):
				if remainingIntegers_multiset[j].element == subset[i].element:
					remainingIntegers_multiset[j].repetition -= subset[i].repetition
					break

			counter = 0
			for i in range(len(remainingIntegers_multiset)):
				counter += remainingIntegers_multiset[i].repetition

			remainingIntegers_array = numpy.empty(counter)
			index = 0
			for i in range(len(remainingIntegers_multiset)):
				for j in range(remainingIntegers_multiset[i].repetition):
					remainingIntegers_array[index] = remainingIntegers_multiset[i].element
					index += 1

			newIntegers = numpy.empty(len(node.subspace.integers))
			index1 = 0
			index2 = len(newIntegers) - counter
			for i in range(len(node.subspace.integers)):
				found = False
				for j in range(len(remainingIntegers_array)):
					if remainingIntegers_array[j] == node.subspace.integers[i]:
						newIntegers[index2] = node.subspace.integers[i]
						index2 += 1
						remainingIntegers_array[j] = -1
						found = True
						break
				
				if found == False:
					newIntegers[index1] = node.subspace.integers[i]
					index1 += 1

			node.subspace.integers = newIntegers


	def computeSumOfMax_splitNoIntegers(self, integers, maxValueForEachSize):
		sumOfMax = numpy.empty(len(integers) + 1)

		sumOfMax[len(integers)] = maxValueForEachSize[integers[-1] - 1][0]

		j = 0
		for i in range(len(integers) - 1, 0, -1):
			if integers[i - 1] == integers[i]:
				j += 1
			
			else:
				j = 0

			sumOfMax[i] = sumOfMax[i+1] + maxValueForEachSize[integers[i-1] - 1][j]

		return sumOfMax

	
	def computeSumOfMax_splitOneInteger(self, node, maxValueForEachSize):
		if node.subspace.relevantNodes == None:
			return self.computeSumOfMax_splitNoIntegers(node.subspace.integers, maxValueForEachSize)

		integers = node.subspace.integers
		sumOfMax = numpy.empty(len(integers) + 1)

		maxUB = node.subspace.UB
		for i in range(len(node.subspace.relevantNodes)):
			if maxUB < node.subspace.relevantNodes[i].subspace.UB:
				maxUB = node.subspace.relevantNodes[i].subspace.UB

		sumOfMax[len(integers)] = maxValueForEachSize[integers[-1] -1][0] + maxUB - node.subspace.UB
		max_f = self.maxF[integers[-1] -1]
		if max_f != 0 and sumOfMax[len(integers)] > max_f:
			sumOfMax[len(integers)] = max_f

		sumOfMax[len(integers) - 1] = sumOfMax[len(integers)] + maxValueForEachSize[integers[-2] - 1][0]
		k = 2

		x = len(integers) - k
		j = 0
		for i in range(x, 0, -1):
			if integers[i-1] == integers[i]:
				j += 1
			else:
				j = 0

			sumOfMax[i] = sumOfMax[i + 1] + maxValueForEachSize[integers[i-1] - 1][j]
			k += 1

		return sumOfMax 


	# ODP functions
	def updateDPSolution(self, CS, value):
		print(self.dpValueOfBestCSFound)
		print(value)
		if self.dpValueOfBestCSFound <= value:
			self.dpValueOfBestCSFound = value
			self.dpBestCSFound = CS[:]

	def getBestHalf(self, coalitionInBitFormat):
		valueOfBestSplit = self.f[coalitionInBitFormat]
		bestFirstHalfInBitFormat = coalitionInBitFormat

		bit = numpy.zeros(self.numPlayers + 1, dtype=int)
		for i in range(self.numPlayers):
			bit[i+1] = 1 << i

		coalitionInByteFormat = self.getGroupFromBitFormat(coalitionInBitFormat)
		coalitionSize = len(coalitionInByteFormat)

		#print(coalitionInByteFormat)
		#input()

		for sizeOfFirstHalf in range(math.ceil(coalitionSize / 2.0), coalitionSize):
			sizeOfSecondHalf = coalitionSize - sizeOfFirstHalf

			if (sizeOfFirstHalf > self.maxNumberOfPlayersPerGroup or sizeOfFirstHalf < self.minNumberOfPlayersPerGroup) and \
				(sizeOfSecondHalf > self.maxNumberOfPlayersPerGroup or sizeOfSecondHalf < self.minNumberOfPlayersPerGroup):
				continue

			numOfPossibilities = 0
			if (coalitionSize % 2) == 0 and sizeOfFirstHalf == sizeOfSecondHalf:
				numOfPossibilities = (int)(math.comb(coalitionSize, sizeOfFirstHalf) / 2)
			
			else:
				numOfPossibilities = math.comb(coalitionSize, sizeOfFirstHalf)

			indicesOfMembersOfFirstHalf = numpy.zeros(sizeOfFirstHalf, dtype=int)
			for i in range(sizeOfFirstHalf):
				indicesOfMembersOfFirstHalf[i] = i + 1

			firstHalfInBitFormat = 0
			for i in range(sizeOfFirstHalf):
				firstHalfInBitFormat += bit[coalitionInByteFormat[indicesOfMembersOfFirstHalf[i] - 1]]

			secondHalfInBitFormat = coalitionInBitFormat - firstHalfInBitFormat

			curValue = self.f[firstHalfInBitFormat] + self.f[secondHalfInBitFormat]

			if curValue > valueOfBestSplit:
				bestFirstHalfInBitFormat = firstHalfInBitFormat
				valueOfBestSplit = curValue

			elif curValue == valueOfBestSplit:
				sizeOfBestFirstHalf = self.getSizeOfCombinationInBitFormat(bestFirstHalfInBitFormat)
				if sizeOfBestFirstHalf > self.maxNumberOfPlayersPerGroup or sizeOfBestFirstHalf < self.minNumberOfPlayersPerGroup:
					if sizeOfFirstHalf <= self.maxNumberOfPlayersPerGroup and sizeOfFirstHalf >= self.minNumberOfPlayersPerGroup:
						bestFirstHalfInBitFormat = firstHalfInBitFormat
						valueOfBestSplit = curValue
				
					elif sizeOfSecondHalf <= self.maxNumberOfPlayersPerGroup and sizeOfSecondHalf >= self.minNumberOfPlayersPerGroup:
						bestFirstHalfInBitFormat = secondHalfInBitFormat
						valueOfBestSplit = curValue
		
			for j in range(1, numOfPossibilities):
				self.getPreviousCombination(coalitionSize, sizeOfFirstHalf, indicesOfMembersOfFirstHalf)

				firstHalfInBitFormat = 0
				for i in range(sizeOfFirstHalf):
					firstHalfInBitFormat += bit[coalitionInByteFormat[indicesOfMembersOfFirstHalf[i]-1]]

				secondHalfInBitFormat = coalitionInBitFormat - firstHalfInBitFormat

				curValue = self.f[firstHalfInBitFormat] + self.f[secondHalfInBitFormat]

				if curValue > valueOfBestSplit:
					bestFirstHalfInBitFormat = firstHalfInBitFormat
					valueOfBestSplit = curValue

				elif curValue == valueOfBestSplit:
					sizeOfBestFirstHalf = self.getSizeOfCombinationInBitFormat(bestFirstHalfInBitFormat)
					if sizeOfBestFirstHalf > self.maxNumberOfPlayersPerGroup or sizeOfBestFirstHalf < self.minNumberOfPlayersPerGroup:
						if sizeOfFirstHalf <= self.maxNumberOfPlayersPerGroup and sizeOfFirstHalf >= self.minNumberOfPlayersPerGroup:
							bestFirstHalfInBitFormat = firstHalfInBitFormat
							valueOfBestSplit = curValue
					
						elif sizeOfSecondHalf <= self.maxNumberOfPlayersPerGroup and sizeOfSecondHalf >= self.minNumberOfPlayersPerGroup:
							bestFirstHalfInBitFormat = secondHalfInBitFormat
							valueOfBestSplit = curValue

		return bestFirstHalfInBitFormat

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
			self.f[coalition] = currQuality


	def evaluateSplits(self, coalition, coalitionSize):
		curValue = -1

		coalitionInBitFormat = self.convertCoalitionFromByteToBitFormat(coalition, coalitionSize)
		
		bestValue = self.f[coalitionInBitFormat]
		firstHalfInBitFormat = coalitionInBitFormat - 1 & coalitionInBitFormat
		secondHalfInBitFormat = 0
		start = 0
		end = 0
		while True:
			#start = time.time()
			secondHalfInBitFormat = coalitionInBitFormat^firstHalfInBitFormat
			#end = time.time()
			#print("1st: ", end - start)

			#start = time.time()
			curValue = self.f[firstHalfInBitFormat] + self.f[secondHalfInBitFormat]
			#end = time.time()
			#print("2nd: ", end - start)
			
			if bestValue <= curValue:
				#start = time.time()
				bestValue = curValue
				#end = time.time()
				#print("3rd: ", end - start)
			
			#start = time.time()
			if firstHalfInBitFormat & (firstHalfInBitFormat - 1) == 0:
				#end = time.time()
				#print("4th: ", end - start)
				break
			#end = time.time()
			#print("4th: ", end - start)

			#start = time.time()
			firstHalfInBitFormat = firstHalfInBitFormat - 1 & coalitionInBitFormat
			#end = time.time()
			#print("5th: ", end - start)

		self.f[coalitionInBitFormat] = bestValue

	def evaluateSplitsOfGrandCoalition(self):
		curValue = -1
		bestValue = -1
		bestHalfOfGrandCoalition = -1
		numCoalitions = 1 << self.numPlayers
		grandCoalition = (1 << self.numPlayers) - 1

		for firstHalfOfGrandCoalition in range((int)(numCoalitions/2 - 1), numCoalitions):

			curSize = self.getSizeOfCombinationInBitFormat(firstHalfOfGrandCoalition)

			if curSize > self.maxNumberOfPlayersPerGroup or curSize < self.minNumberOfPlayersPerGroup:
				continue
			
			secondHalfOfGrandCoalition = numCoalitions - 1 - firstHalfOfGrandCoalition
			curValue = self.f[firstHalfOfGrandCoalition] + self.f[secondHalfOfGrandCoalition]

			if curValue > bestValue:
				bestValue = curValue
				bestHalfOfGrandCoalition = firstHalfOfGrandCoalition

		curValue = self.f[grandCoalition]
		if curValue > bestValue:
			bestValue = curValue
			bestHalfOfGrandCoalition = grandCoalition

		return bestHalfOfGrandCoalition

	def getOptimalSplit(self, coalitionInBitFormat, bestHalfOfCoalition):
		optimalSplit = []
		if (bestHalfOfCoalition == coalitionInBitFormat):
			optimalSplit.append(coalitionInBitFormat)

		else:
			arrayOfBestHalf = numpy.empty(2, dtype=int)
			arrayOfOptimalSplit = numpy.empty(2, dtype=list)
			arrayOfCoalitionInBitFormat = numpy.empty(2, dtype=int)

			arrayOfCoalitionInBitFormat[0] = bestHalfOfCoalition
			arrayOfCoalitionInBitFormat[1] = coalitionInBitFormat - bestHalfOfCoalition

			for i in range(2):
				arrayOfBestHalf[i] = self.getBestHalf(arrayOfCoalitionInBitFormat[i])

				arrayOfOptimalSplit[i] = self.getOptimalSplit(arrayOfCoalitionInBitFormat[i], arrayOfBestHalf[i])

			optimalSplit = numpy.empty(len(arrayOfOptimalSplit[0]) + len(arrayOfOptimalSplit[1]), dtype=int)
			k = 0
			for i in range(2):
				lenOfOptimalSplit = len(arrayOfOptimalSplit[i])
				for j in range(lenOfOptimalSplit):
					optimalSplit[k] = arrayOfOptimalSplit[i][j]
					k += 1

		return optimalSplit

	def getOptimalSplitFromCS(self, CS):
		optimalSplit = [[] for _ in range(len(CS))]
		numOfCoalitionsInFinalResult = 0

		for i in range(len(CS)):
			coalitionInBitFormat = self.convertCoalitionFromByteToBitFormat(CS[i], len(CS[i]))
			bestHalfOfCoalitionInBitFormat = self.getBestHalf(coalitionInBitFormat)
			optimalSplit[i] = self.getOptimalSplit(coalitionInBitFormat, bestHalfOfCoalitionInBitFormat)
			numOfCoalitionsInFinalResult += len(optimalSplit[i])

		finalResult = [[] for _ in range(numOfCoalitionsInFinalResult)]
		k = 0
		for i in range(len(CS)):
			for j in range(len(optimalSplit[i])):
				finalResult[k] = self.getGroupFromBitFormat(optimalSplit)
				k += 1

		return finalResult


	def initPascalMatrix(self, numOfLines, numOfColumns):
		
		if self.pascalMatrix == [] or numOfLines > len(self.pascalMatrix):
			
			if self.pascalMatrix == []:
				self.pascalMatrix = numpy.ones((numOfLines, numOfColumns), dtype=numpy.int64)
				for j in range(1, numOfColumns):
					self.pascalMatrix[0][j] = j + 1

				for i in range(1, numOfLines):
					for j in range(1, numOfColumns):
						self.pascalMatrix[i][j] = self.pascalMatrix[i-1][j] + self.pascalMatrix[i][j-1]

		return self.pascalMatrix


	def getCombinationAtGivenIndex(self, size, index):
		index += 1
		self.initPascalMatrix(self.numPlayers + 1, self.numPlayers + 1)
		M = numpy.zeros(size, dtype=int)

		j = 1
		s1 = size

		while True:
			x = 1
			while self.pascalMatrix[s1-1][x-1] < index:
				x += 1
			
			M[j-1] = (int)((self.numPlayers - s1 + 1) - x + 1)

			if self.pascalMatrix[s1-1][x-1] == index:
				for k in range(j, size):
					M[k] = (int)(M[k-1] + 1)
				break

			else:
				j += 1
				index -= self.pascalMatrix[s1-1][x-2]
				s1 -= 1
		
		return M

	
	def getPreviousCombination(self, numPlayers, size, coalition):

		maxPossibleValueForFirstAgent = numPlayers - size + 1
		for i in range(size-1, -1, -1):
			if coalition[i] < maxPossibleValueForFirstAgent+i:
				coalition[i] += 1
				for j in range(i+1, size):
					coalition[j] = coalition[j-1] + 1
				break

	def distributeRemainingPlayers(self, coalitionStructure):
		remainingPlayers = []
		for i in range(len(coalitionStructure)):
			if len(coalitionStructure[i]) < self.minNumberOfPlayersPerGroup:
				remainingPlayers = coalitionStructure[i]
				coalitionStructure = numpy.delete(coalitionStructure, [i])
				break

		for player in remainingPlayers:
			bestImprovement = -1
			bestCoalition = []
			bestIndex = -1
			tempCoalition = []

			for i in range(len(coalitionStructure)):
				if len(coalitionStructure[i]) <= self.maxNumberOfPlayersPerGroup:

					tempCoalition = coalitionStructure[i][:]
					tempCoalition.append(player)
					tempCoalition.sort()
					value = self.f[self.convertCoalitionFromByteToBitFormat(tempCoalition, len(tempCoalition))]
					if value > bestImprovement:
						bestImprovement = value
						bestCoalition = tempCoalition[:]
						bestIndex = i

			coalitionStructure[bestIndex] = bestCoalition[:]
		
		return coalitionStructure

	def finalize(self):
		if self.dpBestCSFound is not None:
			self.updateIPSolution(self.dpBestCSFound, self.dpValueOfBestCSFound)

		return self.ipBestCSFound

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

	def IP(self):
		self.searchFirstAndLastLevel()

		avgValueForEachSize = self.computeAvgForEachSize()

		maxValueForEachSize = self.setMaxValueForEachSize()

		subspaces = self.initSubspaces(avgValueForEachSize, maxValueForEachSize)
		self.ipIntegerPartitionGraph = IntegerPartitionGraph(subspaces, self.numPlayers, 1)

		self.totalNumOfExapnsions = self.computeTotalNumOfExpansions()

		numOfRemainingSubspaces = IntegerPartition.getNumOfIntegerPartitions(self.numPlayers)
		print("Num of remaining subspaces: ", numOfRemainingSubspaces)

		#breakpoint()

		numOfRemainingSubspaces -= self.disableSubspacesThatWereSearchedInTheBeginning()

		self.setUpperAndLowerBoundsOnOptimalValue()
		print("Num of remaining subspaces: ", numOfRemainingSubspaces)

		numOfRemainingSubspaces -= self.disableSubspacesWithUBLowerThanTheHighestLB()
		
		print("Num of remaining subspaces: ", numOfRemainingSubspaces)
		print("Best CS Found: ", self.ipBestCSFound, " with value: ", self.ipValueOfBestCSFound)

		if numOfRemainingSubspaces == 0:
			return

		self.ODP()
		acceptableValue = self.ipUpperBoundOnOptimalValue
		sortedNodes = self.getListOfSortedNodes(subspaces)

		print(acceptableValue)

		while self.ipLowerBoundOnOptimalValue < acceptableValue:


			self.ipIntegerPartitionGraph.updateEdges(self.numPlayers, self.odpMaxSizeComputedSoFar)

			numOfRemainingSubspaces -= self.disableSubspacesReachableFromBottomNode()

			#breakpoint()
			nodeToBeSearched = self.getFirstEnabledNode(sortedNodes)
			if nodeToBeSearched == None:
				break

			subsetToBePutAtTheBeginning = self.getRelevantNodes(nodeToBeSearched, 1)

			self.putSubsetAtTheBeginning(nodeToBeSearched, subsetToBePutAtTheBeginning)

			sumOfMax = self.computeSumOfMax_splitOneInteger(nodeToBeSearched, maxValueForEachSize)

			numOfIntegersToSplit = 0
			if subsetToBePutAtTheBeginning != None:
				numOfIntegersToSplit = len(nodeToBeSearched.subspace.integers) - ODPIP.getCardinalityOfMultiset(subsetToBePutAtTheBeginning)
			numOfRemainingSubspaces -= nodeToBeSearched.subspace.search(self, self.odpHasFinished, acceptableValue, sumOfMax, numOfIntegersToSplit)

			self.setUpperAndLowerBoundsOnOptimalValue()
			acceptableValue = self.ipUpperBoundOnOptimalValue

			if self.ipLowerBoundOnOptimalValue < self.ipValueOfBestCSFound:
				self.ipLowerBoundOnOptimalValue = self.ipValueOfBestCSFound
				numOfRemainingSubspaces -= self.disableSubspacesWithUBLowerThanTheHighestLB()

			if numOfRemainingSubspaces == 0:
				break

		
		print("Done")
		return self.finalize()


	def organize(self):
		self.playerIds = sorted(self.playerModelBridge.getAllPlayerIds())
		self.numPlayers = len(self.playerIds)

		self.tooManyPlayers = (self.numPlayers % self.maxNumberOfPlayersPerGroup != 0)

		self.coalitionsProfiles = numpy.empty(1 << self.numPlayers, dtype=InteractionsProfile)
		self.coalitionsAvgCharacteristics = numpy.empty(1 << self.numPlayers, dtype=PlayerCharacteristics)
		self.coalitionsValues = numpy.empty(1 << self.numPlayers)
		self.f = numpy.empty(1 << self.numPlayers)
		self.maxF = numpy.empty(self.numPlayers)

		self.dpMaxSizeComputedSoFar = 0

		# estimate preferences
		self.persEstAlg.updateEstimates()

		# initialization(compute the value for every coalition between min and max number of players)
		self.computeAllCoalitionsValues()

		print("Starting ODPIP...")
		bestCSFound_bitFormat = (gs.odpip(self.numPlayers, self.minNumberOfPlayersPerGroup, self.maxNumberOfPlayersPerGroup, self.coalitionsValues.tolist()))
		#bestCSFound_byteFormat = self.IP()
		bestCSFound_byteFormat = self.convertSetOfCombinationsFromBitFormat(bestCSFound_bitFormat)
		return self.results(bestCSFound_byteFormat)

	def ODP(self):
		prevTime = time.time()
		grandCoalition = (1 << self.numPlayers) - 1
		bestHalfOfGrandCoalition = -1

		self.dpMaxSizeComputedSoFar += 1
		# evaluate the possible splits of every coalition of size 2, 3, ...
		for curSize in range(2, self.numPlayers+1):
			if math.floor(2 * self.numPlayers / 5.0) < curSize and curSize < self.numPlayers: 
				continue
				
			if curSize < self.numPlayers:
				numOfCoalitionsOfCurSize = math.comb(self.numPlayers, curSize)

				curCoalition = self.getCombinationAtGivenIndex(curSize, numOfCoalitionsOfCurSize - 1)
				self.evaluateSplits(curCoalition, curSize)

				for _ in range(1, numOfCoalitionsOfCurSize):
					self.getPreviousCombination(self.numPlayers, curSize, curCoalition)
					self.evaluateSplits(curCoalition, curSize)


			else:
				bestHalfOfGrandCoalition = self.evaluateSplitsOfGrandCoalition()

			if curSize < self.numPlayers:
				bestHalfOfGrandCoalition = self.evaluateSplitsOfGrandCoalition()
				bestCSFoundSoFar = self.getOptimalSplit(grandCoalition, bestHalfOfGrandCoalition)
				#print(bestCSFoundSoFar)
				bestCSFoundSoFar_byteFormat = self.convertSetOfCombinationsFromBitFormat(bestCSFoundSoFar)
				self.updateDPSolution(bestCSFoundSoFar_byteFormat, self.getCoalitionStructureInByteFormatValue(bestCSFoundSoFar_byteFormat))
				self.updateIPSolution(bestCSFoundSoFar_byteFormat, self.getCoalitionStructureInByteFormatValue(bestCSFoundSoFar_byteFormat))


			print("size", curSize, "took: ", time.time() - prevTime)
					#print("Best coalition found so far", bestCSFoundSoFar_byteFormat)
			prevTime = time.time()

		#print(time.time() - start)

		bestCSFound = self.getOptimalSplit(grandCoalition, bestHalfOfGrandCoalition)
		bestCSFound_byteFormat = self.convertSetOfCombinationsFromBitFormat(bestCSFound)
		if self.tooManyPlayers:
			bestCSFound_byteFormat = self.distributeRemainingPlayers(bestCSFound_byteFormat)
			
		print(bestCSFound_byteFormat)
		return bestCSFound_byteFormat
