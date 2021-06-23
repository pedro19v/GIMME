import random
import math
import copy
import numpy
from abc import ABC, abstractmethod
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

		self.updateMetrics(newGroups)
		return {"groups": newGroups, "profiles": newConfigProfiles, "avgCharacteristics": newAvgCharacteristics}




class SimulatedAnnealingConfigsGen(ConfigsGenAlg):

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


		# estimate personalities
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

				# generate group profile as random or average of the personalities estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()

				if(random.uniform(0.0, 1.0) > self.temperature):
					for currPlayer in group:
						personality = self.playerModelBridge.getPlayerPersonalityEst(currPlayer)
						for dim in profile.dimensions:
							profile.dimensions[dim] += personality.dimensions[dim] / groupSize
					profile.normalize()
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


		if(self.temperature > 0.0):
			self.temperature -= self.temperatureDecay
		else:
			self.temperature = 1.0

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}




class StochasticHillclimberConfigsGen(ConfigsGenAlg):

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


		# estimate personalities
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

				# generate profile as average of the personalities estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()

				for currPlayer in group:
					personality = self.playerModelBridge.getPlayerPersonalityEst(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += (personality.dimensions[dim] / groupSize)

				# print("profile in-configGen: "+str(profile.dimensions)+";groupSize: "+str(groupSize))
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




class SimpleConfigsGenVer2(ConfigsGenAlg):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg, 
		numTestedGroupProfiles = None, 
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
		self.numTestedGroupProfiles = 100 if numTestedGroupProfiles == None else numTestedGroupProfiles 
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

				# generate random profile set, pick best
				bestProfile = self.interactionsProfileTemplate.generateCopy().reset()
				profile = bestProfile

				currInnerQuality = 0.0
				currMaxInnerQuality = -float("inf")
				
				currAvgCharacteristics = PlayerCharacteristics().reset()
				
				for i in range(self.numTestedGroupProfiles):
					currInnerAvgCharacteristics =  PlayerCharacteristics().reset()
					profile = self.interactionsProfileTemplate.generateCopy().randomize()
					# calculate fitness and average state
					for currPlayer in group:

						currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
						currState.profile = profile

						currInnerAvgCharacteristics.ability += currState.characteristics.ability / groupSize
						currInnerAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
					
						currInnerQuality += self.calcQuality(self.regAlg.predict(profile, currPlayer))


					if currInnerQuality >= currMaxInnerQuality:
						currMaxInnerQuality = currInnerQuality
						bestProfile = profile

				currAvgCharacteristics = currInnerAvgCharacteristics
				currQuality += currMaxInnerQuality
				newAvgCharacteristics.append(currAvgCharacteristics)
				newConfigProfiles.append(profile)

			if (currQuality > currMaxQuality):
				bestGroups = newGroups
				bestConfigProfiles = newConfigProfiles
				bestAvgCharacteristics = newAvgCharacteristics
				currMaxQuality = currQuality

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}




class SimpleConfigsGenVer1(ConfigsGenAlg):

	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg, 
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

				# generate random profile set, pick best
				bestProfile = self.interactionsProfileTemplate.generateCopy().reset()
				profile = bestProfile

				currInnerQuality = 0.0
				currMaxInnerQuality = -float("inf")
				
				currAvgCharacteristics = PlayerCharacteristics().reset()
				
				currInnerAvgCharacteristics =  PlayerCharacteristics().reset()
				profile = self.interactionsProfileTemplate.generateCopy().randomize()
				# calculate fitness and average state
				for currPlayer in group:

					currState = self.playerModelBridge.getPlayerCurrState(currPlayer)
					currState.profile = profile

					currInnerAvgCharacteristics.ability += currState.characteristics.ability / groupSize
					currInnerAvgCharacteristics.engagement += currState.characteristics.engagement / groupSize
				
					currInnerQuality += self.calcQuality(self.regAlg.predict(profile, currPlayer))


				if currInnerQuality >= currMaxInnerQuality:
					currMaxInnerQuality = currInnerQuality
					bestProfile = profile

				currAvgCharacteristics = currInnerAvgCharacteristics
				currQuality += currMaxInnerQuality
				newAvgCharacteristics.append(currAvgCharacteristics)
				newConfigProfiles.append(profile)

			if (currQuality > currMaxQuality):
				bestGroups = newGroups
				bestConfigProfiles = newConfigProfiles
				bestAvgCharacteristics = newAvgCharacteristics
				currMaxQuality = currQuality

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}





class AccurateConfigsGen(ConfigsGenAlg):

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

				# generate profile as average of the personalities estimates
				profile = self.interactionsProfileTemplate.generateCopy().reset()
				for currPlayer in group:
					personality = self.playerModelBridge.getPlayerRealPersonality(currPlayer)
					for dim in profile.dimensions:
						profile.dimensions[dim] += personality.dimensions[dim] / groupSize
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

		self.updateMetrics(bestGroups)
		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": bestAvgCharacteristics}



from deap import base, creator, tools, algorithms
from collections import *

class EvolutionaryConfigsGenDEAP(ConfigsGenAlg):
	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg = None, 
		numberOfConfigChoices = None, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None, 
		qualityWeights = None, 
		probOfCross = None, 
		probOfMutation = None, 
		numFitSurvivors = None):

		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.numberOfConfigChoices = 100 if numberOfConfigChoices == None else numberOfConfigChoices 

		self.numFitSurvivors = 10 if numFitSurvivors == None else numFitSurvivors
		self.probOfCross = 0.7 if probOfCross == None else probOfCross
		self.probOfMutation = 0.2 if probOfMutation == None else probOfMutation

		if(regAlg==None):
			regAlg = KNNRegression(playerModelBridge, 5)

		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights

		self.initGenAlg()


	def randomIndividualGenerator(self, playerIds, minNumGroups, maxNumGroups):
		groups = self.randomConfigGenerator(playerIds, minNumGroups, maxNumGroups)
		profs = [self.randomProfileGenerator() for i in range(len(groups))]
		return [groups, [val for sublist in profs for val in sublist]]

	def randomProfileGenerator(self):
		return self.interactionsProfileTemplate.randomized().flattened()



	def cxGIMME(self, ind1, ind2):
		# configs
		config1 = ind1[0]
		config2 = ind2[0]

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

			cxpoint = 2 #random.randint(1,minLen - 1)
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





		# profiles
		prof1 = ind1[1]
		prof2 = ind2[1]

		newProfiles = tools.cxBlend(prof1, prof2, 0.5)

		#the inds become offsprings
		ind1[0] = newConfigs[0] 
		ind1[1] = newProfiles[0]
		ind2[0] = newConfigs[1] 
		ind2[1] = newProfiles[1]

		return (ind1, ind2)


	def mutGIMME(self, individual, indpb):
		#only mutate GIPs for now
		prof = individual[1]
		individual[1] = tools.mutShuffleIndexes(prof, indpb)
		return individual,

	def reset(self):
		super().reset()
		self.initGenAlg()

	def calcFitness(self, individual):
		config = individual[0]
		profiles = individual[1]
		profiles = [profiles[x:x+2] for x in range(0, len(profiles), 2)]

		print(profiles)
		for groupI in range(len(config)):
			
			group = config[groupI]
			flatProfile = profiles[groupI]

			#unflatten profile
			profile = self.interactionsProfileTemplate.unflattened(array = flatProfile)
			totalFitness = 0

			for playerId in group:
				predictedIncreases = self.regAlg.predict(profile, playerId)
				totalFitness += self.qualityWeights.ability*predictedIncreases.characteristics.ability + self.qualityWeights.engagement*predictedIncreases.characteristics.engagement

		return totalFitness, #must return a tuple

	
	def initGenAlg(self):
		playerIds = self.playerModelBridge.getAllPlayerIds() 
		minNumGroups = math.ceil(len(playerIds) / self.maxNumberOfPlayersPerGroup)
		maxNumGroups = math.floor(len(playerIds) / self.minNumberOfPlayersPerGroup)

		creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
		creator.create("Individual", list, typecode='i', fitness=creator.FitnessMin)

		self.toolbox = base.Toolbox()

		self.toolbox.register("indices", self.randomIndividualGenerator, playerIds, minNumGroups, maxNumGroups)
		# toolbox.register("indices", [toolbox.group, toolbox.profile])

		self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.indices)
		self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

		self.toolbox.register("mate", self.cxGIMME)
		self.toolbox.register("mutate", self.mutGIMME, indpb=self.probOfMutation)
		self.toolbox.register("select", tools.selTournament, tournsize=self.numFitSurvivors)
		self.toolbox.register("evaluate", self.calcFitness)

		# random.seed(169)

		self.pop = self.toolbox.population(n = self.numberOfConfigChoices)
		self.hof = tools.HallOfFame(1)

	def organize(self):
		
		algorithms.eaSimple(self.pop, self.toolbox, cxpb=self.probOfCross, mutpb=self.probOfMutation, ngen=500, halloffame = self.hof)
		breakpoint()

		return {"groups": bestGroups, "profiles": bestConfigProfiles, "avgCharacteristics": [PlayerCharacteristics() for i in range(maxNumGroups)]}




class EvolutionaryConfigsGenLegacy(ConfigsGenAlg):
	def __init__(self, 
		playerModelBridge, 
		interactionsProfileTemplate, 
		regAlg = None, 
		numberOfConfigChoices = None, 
		preferredNumberOfPlayersPerGroup = None, 
		minNumberOfPlayersPerGroup = None, 
		maxNumberOfPlayersPerGroup = None, 
		fitnessWeights = None, 
		numMutations = None, 
		probOfMutation = None, 
		numFitSurvivors = None):

		super().__init__(
			playerModelBridge = playerModelBridge,
			interactionsProfileTemplate = interactionsProfileTemplate, 
			preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
			minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup, 
			maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup)

		self.regAlg = regAlg
		self.numberOfConfigChoices = 100 if numberOfConfigChoices == None else numberOfConfigChoices 

		self.populationInited = False
		self.numMutations = 4 if numMutations == None else numMutations
		self.numFitSurvivors = 10 if numFitSurvivors == None else numFitSurvivors
		self.probOfMutation = 0.1 if probOfMutation == None else probOfMutation

		if(regAlg==None):
			regAlg = KNNRegression(playerModelBridge, 5)

		self.fitnessWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights == None else qualityWeights

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
