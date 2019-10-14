from abc import ABC, abstractmethod


class RegressionAlg(ABC):

	@abstractmethod
	def predict(profile, player):
		pass

# ---------------------- KNNRegression stuff ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, numberOfNNs):
		self.numberOfNNs = numberOfNNs;

	def interactionsProfileSort(pState1, pState2):

		dist1 = testedProfile.distanceBetween(pState1.profile)
		dist2 = testedProfile.distanceBetween(pState2.profile)

		pState1.dist = dist1
		pState2.dist = dist2

		return dist1 < dist2

	def predict(profile, player):
		pastModelIncs = player.getPastModelIncreases()
		pastModelIncsCopy = pastModelIncs.copy()
		pastModelIncsSize = len(pastModelIncs)

		predictedModel = PlayerState( profile, PlayerCharacteristics() , 0 )
		predictedModel = sorted(predictedModel, key=InteractionsProfileSort(profile))

		if (pastModelIncsSize > numberOfNNs):
			pastModelIncsCopy = numpy.resize(pastModelIncsCopy, numberOfNNs)
	
		pastModelIncsCopySize = len(pastModelncsCopy)

		for i in range(pastModelncsCopySize):
			pastProfile = pastModelIncsCopy[i].profile;
			distance = profile.distanceBetween(pastProfile);

			predictedModel.characteristics.ability += (pastModelncsCopy[i].characteristics.ability* (1 - distance)) / (double)(pastModelncsCopySize); #* (1 - distance) 
			predictedModel.characteristics.engagement += (pastModelncsCopy[i].characteristics.engagement* (1 - distance)) / (double)(pastModelncsCopySize); #* (1 - distance)
		
		return predictedModel;


# ---------------------- NeuralNetworkRegression stuff ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	def predict(profile, player):
		pass


# ---------------------- ReinforcementLearningRegression stuff ---------------------------
class ReinforcementLearningRegression(RegressionAlg):

	def predict(profile, player):
		pass

