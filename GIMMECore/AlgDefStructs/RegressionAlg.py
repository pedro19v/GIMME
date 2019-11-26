from abc import ABC, abstractmethod
import copy
from PlayerStructs import *
import json

class RegressionAlg(ABC):

	@abstractmethod
	def predict(self, playerModelBridge, profile, playerId):
		pass


# ---------------------- KNNRegression stuff ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, numberOfNNs):
		self.numberOfNNs = numberOfNNs

	def distSort(self, elem):
		return elem.dist

	def creationTimeSort(self, elem):
		return elem.creationTime

	def predict(self, playerModelBridge, profile, playerId):

		pastModelIncs = playerModelBridge.getPlayerPastModelIncreases(playerId).getAllStates()
		pastModelIncsCopy = copy.deepcopy(pastModelIncs)
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(0, profile = profile, characteristics = PlayerCharacteristics())
	
		for modelInc in pastModelIncsCopy:
			modelInc.dist = profile.sqrDistanceBetween(modelInc.profile)


		pastModelIncsCopy = sorted(pastModelIncsCopy, key=self.distSort)

		numberOfIterations = min(self.numberOfNNs, len(pastModelIncsCopy))
		pastModelIncsCopy = pastModelIncsCopy[:numberOfIterations]
		pastModelIncsCopy = sorted(pastModelIncsCopy, key=self.creationTimeSort)
		
		# print(json.dumps(pastModelIncsCopy, default=lambda o: o.__dict__["dist"], sort_keys=True))

		for i in range(numberOfIterations):
			currState = pastModelIncsCopy[i]
			pastCharacteristics = currState.characteristics

			predictedState.characteristics.ability += pastCharacteristics.ability / numberOfIterations * ((numberOfIterations - i)/numberOfIterations)
			predictedState.characteristics.engagement += pastCharacteristics.engagement/ numberOfIterations * ((numberOfIterations - i)/numberOfIterations)
		
		# print(json.dumps(predictedState, default=lambda o: o.__dict__, sort_keys=True))
		return predictedState


# ---------------------- NeuralNetworkRegression stuff ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	def predict(self, playerModelBridge, profile, playerId):
		pass


# ---------------------- ReinforcementLearningRegression stuff ---------------------------
class ReinforcementLearningRegression(RegressionAlg):

	def predict(self, playerModelBridge, profile, playerId):
		pass

