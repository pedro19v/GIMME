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

	def interactionsProfileSort(self, pState1, pState2):

		dist1 = testedProfile.distanceBetween(pState1.profile)
		dist2 = testedProfile.distanceBetween(pState2.profile)

		pState1.dist = dist1
		pState2.dist = dist2

		return dist1 < dist2

	def predict(self, profile, playerModelBridge, playerId):

		pastModelIncs = playerModelBridge.getPlayerPastModelIncreases(playerId).cells
		pastModelIncsCopy = copy.deepcopy(pastModelIncs)
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(profile, PlayerCharacteristics())
		# predictedState = sorted(predictedState, key=self.interactionsProfileSort(profile))

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

