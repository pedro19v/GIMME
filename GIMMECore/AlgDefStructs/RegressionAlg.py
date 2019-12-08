from abc import ABC, abstractmethod
import copy
from ..PlayerStructs import *
import json

class RegressionAlg(ABC):

	def __init__(self, playerModelBridge):
		self.playerModelBridge = playerModelBridge

	@abstractmethod
	def predict(self, profile, playerId):
		pass


# ---------------------- KNNRegression stuff ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, playerModelBridge, numberOfNNs):
		super().__init__(playerModelBridge)
		self.numberOfNNs = numberOfNNs

	def distSort(self, elem):
		return elem.dist

	def creationTimeSort(self, elem):
		return elem.creationTime

	def predict(self, profile, playerId):

		pastModelIncs = self.playerModelBridge.getPlayerStateGrid(playerId).getAllStates()
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(profile = profile, characteristics = PlayerCharacteristics())
	
		for modelInc in pastModelIncs:
			modelInc.dist = profile.sqrDistanceBetween(modelInc.profile)

		pastModelIncs = sorted(pastModelIncs, key=self.distSort)

		numberOfIterations = min(self.numberOfNNs, len(pastModelIncs))
		pastModelIncs = pastModelIncs[:numberOfIterations]
		pastModelIncs = sorted(pastModelIncs, key=self.creationTimeSort)
		
		for i in range(numberOfIterations):
			currState = pastModelIncs[i]
			pastCharacteristics = currState.characteristics

			predictedState.characteristics.ability += pastCharacteristics.ability / numberOfIterations * ((numberOfIterations - i)/numberOfIterations)
			predictedState.characteristics.engagement += pastCharacteristics.engagement/ numberOfIterations * ((numberOfIterations - i)/numberOfIterations)
		
		return predictedState


# ---------------------- NeuralNetworkRegression stuff ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	# possible TODO

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass


# ---------------------- ReinforcementLearningRegression stuff ---------------------------
class ReinforcementLearningRegression(RegressionAlg):

	# possible TODO

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass

