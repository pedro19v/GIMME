import copy
import json

from abc import ABC, abstractmethod
from ..PlayerStructs import *

from sklearn import linear_model, neighbors

class RegressionAlg(ABC):

	def __init__(self, playerModelBridge):
		self.playerModelBridge = playerModelBridge

	@abstractmethod
	def predict(self, profile, playerId):
		pass


# ---------------------- KNNRegression ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, playerModelBridge, numberOfNNs):
		super().__init__(playerModelBridge)
		self.numberOfNNs = numberOfNNs

	def distSort(self, elem):
		return elem.dist

	def creationTimeSort(self, elem):
		return elem.creationTime

	def predict(self, profile, playerId):
		# import time
		# startTime = time.time()

		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStates().copy()
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(profile = profile, characteristics = PlayerCharacteristics())
	
		for modelInc in pastModelIncs:
			modelInc.dist = profile.sqrDistanceBetween(modelInc.profile)

		pastModelIncs = sorted(pastModelIncs, key=self.distSort)

		numberOfIterations = min(self.numberOfNNs, len(pastModelIncs))
		pastModelIncs = pastModelIncs[:numberOfIterations]

		triangularNumberOfIt = sum(range(numberOfIterations + 1))
		for i in range(numberOfIterations):
			currState = pastModelIncs[i]
			pastCharacteristics = currState.characteristics
			ratio = (numberOfIterations - i)/triangularNumberOfIt

			predictedState.characteristics.ability += pastCharacteristics.ability * ratio
			predictedState.characteristics.engagement += pastCharacteristics.engagement * ratio

		# executionTime = (time.time() - startTime)
		# print('Execution time in seconds: ' + str(executionTime))
		
		return predictedState

# ---------------------- KNNRegressionSKLearn ---------------------------
class KNNRegressionSKLearn(RegressionAlg):

	def __init__(self, playerModelBridge, numberOfNNs):
		super().__init__(playerModelBridge)
		self.numberOfNNs = numberOfNNs


	def predict(self, profile, playerId):
		# import time
		# startTime = time.time()

		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStatesFlatten()

		lenPMI = len(pastModelIncs['profiles'])
		
		numberOfNNs = self.numberOfNNs
		if(lenPMI < self.numberOfNNs):
			if(lenPMI==0):
				return PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = 0.5, engagement = 0.5))
			numberOfNNs = lenPMI

		profData = profile.flattened()
		prevProfs = pastModelIncs['profiles']
		

		self.regrAb = neighbors.KNeighborsRegressor(numberOfNNs, weights="distance")
		self.regrAb.fit(prevProfs, pastModelIncs['abilities'])
		predAbilityInc = self.regrAb.predict([profData])[0]

		self.regrEng = neighbors.KNeighborsRegressor(numberOfNNs, weights="distance")
		self.regrEng.fit(prevProfs, pastModelIncs['engagements'])
		predEngagement = self.regrEng.predict([profData])[0]

		predState = PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = predAbilityInc, engagement = predEngagement))
		

		# executionTime = (time.time() - startTime)
		# print('Execution time in seconds: ' + str(executionTime))

		return predState

# ---------------------- LinearRegressionSKLearn ---------------------------
class LinearRegressionSKLearn(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		
		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStatesFlatten()

		if(len(pastModelIncs['profiles'])==0):
			return PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = 0.5, engagement = 0.5))

		profData = profile.flattened()

		prevProfs = pastModelIncs['profiles']

		regr = linear_model.LinearRegression() 
		regr.fit(prevProfs, pastModelIncs['abilities'])
		predAbilityInc = regr.predict([profData])[0]

		regr.fit(prevProfs, pastModelIncs['engagements'])
		predEngagement = regr.predict([profData])[0]

		predState = PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = predAbilityInc, engagement = predEngagement))
		return predState

# ---------------------- SVMRegressionSKLearn ---------------------------
class SVMRegressionSKLearn(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		
		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStatesFlatten()

		if(len(pastModelIncs['profiles'])==0):
			return PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = 0.5, engagement = 0.5))

		profData = profile.flattened()

		prevProfs = pastModelIncs['profiles']

		regr = svm.SVR()
		regr.fit(prevProfs, pastModelIncs['abilities'])
		predAbility = regr.predict([profData])[0]

		regr.fit(prevProfs, pastModelIncs['engagements'])
		predEngagement = regr.predict([profData])[0]

		predState = PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = predAbility, engagement = predEngagement))
		return predState

# ---------------------- DecisionTreesRegression ---------------------------
class DecisionTreesRegression(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass


# ---------------------- NeuralNetworkRegression ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass

