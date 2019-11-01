from abc import ABC, abstractmethod
import copy
from PlayerStructs import *

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

		pastModelIncs = playerModelBridge.getPlayerPastModelIncreases(playerId).getAllCells()
		print(pastModelIncs)
		pastModelIncsCopy = copy.deepcopy(pastModelIncs)
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(profile, PlayerCharacteristics())

		for modelInc in pastModelIncsCopy:
			modelInc.dist = profile.distanceBetween(modelInc.profile)

		pastModelIncsCopy = sorted(pastModelIncsCopy, key=self.interactionsProfileSort)

		if (pastModelIncsSize > self.numberOfNNs):
			pastModelIncsCopy = numpy.resize(pastModelIncsCopy, self.numberOfNNs)
	
		pastModelIncsCopySize = len(pastModelIncsCopy)

		for i in pastModelIncsCopy:
			pastProfile = i.profile
			pastCharacteristics = i.characteristics
			distance = profile.distanceBetween(pastProfile)

			predictedState.characteristics.ability += (pastCharacteristics.ability* (1 - distance)) / pastModelIncsCopySize #* (1 - distance) 
			predictedState.characteristics.engagement += (pastCharacteristics.engagement* (1 - distance)) / pastModelIncsCopySize #* (1 - distance)
		
		return predictedState;


# ---------------------- NeuralNetworkRegression stuff ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	def predict(self, profile, playerModelBridge, playerId):
		pass


# ---------------------- ReinforcementLearningRegression stuff ---------------------------
class ReinforcementLearningRegression(RegressionAlg):

	def predict(self, profile, playerModelBridge, playerId):
		pass

