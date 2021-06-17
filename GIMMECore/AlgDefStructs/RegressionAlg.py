import copy
import json

from abc import ABC, abstractmethod
from ..PlayerStructs import *
from sklearn import svm

class RegressionAlg(ABC):

	def __init__(self, playerModelBridge):
		self.playerModelBridge = playerModelBridge

	@abstractmethod
	def predict(self, profile, playerId):
		pass


# ---------------------- KNNRegressionLegacy ---------------------------
class KNNRegressionLegacy(RegressionAlg):

	def __init__(self, playerModelBridge, numberOfNNs):
		super().__init__(playerModelBridge)
		self.numberOfNNs = numberOfNNs

	def distSort(self, elem):
		return elem.dist

	def creationTimeSort(self, elem):
		return elem.creationTime

	def predict(self, profile, playerId):
		pastModelIncs = self.playerModelBridge.getPlayerStateGrid(playerId).getAllStates().copy()
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

		return predictedState

# ---------------------- KNNRegression ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass

# ---------------------- SVMRegression ---------------------------
class SVMRegression(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		
		pastModelIncs = self.playerModelBridge.getPlayerStateGrid(playerId).getAllStatesFlatten().copy()

		regr = svm.SVR()
		profData = [dim for dim in profile.dimensions]

		prevProfs = pastModelIncs['profiles']
		regr.fit(prevProfs, pastModelIncs['ability'])
		print(regr.predict([profData]))

		regr.fit(prevProfs, pastModelIncs['engagement'])
		print(regr.predict([[profData]]))

		predState = PlayerState(profile = predProfile, characteristics = PlayerCharacteristics(ability = predAbility, engagement = predEngagement))
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

