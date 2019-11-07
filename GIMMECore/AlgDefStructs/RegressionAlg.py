from abc import ABC, abstractmethod
import copy
from PlayerStructs import *
import json

class RegressionAlg(ABC):

	@abstractmethod
	def predict(self, profile, playerModelBridge, playerId):
		pass

# ---------------------- KNNRegression stuff ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, numberOfNNs):
		self.numberOfNNs = numberOfNNs;

	def interactionsProfileSort(self, elem):
		return elem.dist

	def predict(self, profile, playerModelBridge, playerId):

		pastModelIncs = playerModelBridge.getPlayerPastModelIncreases(playerId).getAllStates()
		# print(pastModelIncs)
		pastModelIncsCopy = copy.deepcopy(pastModelIncs)
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(profile, PlayerCharacteristics())

		if (pastModelIncsSize > self.numberOfNNs):
			pastModelIncsCopy = numpy.resize(pastModelIncsCopy, self.numberOfNNs)
	
		for modelInc in pastModelIncsCopy:
			modelInc.dist = profile.sqrDistanceBetween(modelInc.profile)

		pastModelIncsCopy = sorted(pastModelIncsCopy, key=self.interactionsProfileSort)
		# print(json.dumps(pastModelIncsCopy, default=lambda o: o.__dict__, sort_keys=True))
		# quit()
		pastModelIncsCopySize = len(pastModelIncsCopy)

		for i in pastModelIncsCopy:
			pastProfile = i.profile
			pastCharacteristics = i.characteristics
			distance = profile.sqrDistanceBetween(pastProfile)

			predictedState.characteristics.ability += (pastCharacteristics.ability* (2 - distance)/2) / pastModelIncsCopySize #* (1 - distance) 
			predictedState.characteristics.engagement += (pastCharacteristics.engagement* (2 - distance)/2) / pastModelIncsCopySize #* (1 - distance)
		
		return predictedState


# ---------------------- NeuralNetworkRegression stuff ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	def predict(self, profile, playerModelBridge, playerId):
		pass


# ---------------------- ReinforcementLearningRegression stuff ---------------------------
class ReinforcementLearningRegression(RegressionAlg):

	def predict(self, profile, playerModelBridge, playerId):
		pass

