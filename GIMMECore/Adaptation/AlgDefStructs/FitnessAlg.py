from abc import ABC, abstractmethod
from Adaptation.AlgDefStructs.RegressionAlg import * 

class FitnessAlg(ABC):
	@abstractmethod
	def calculate(player, interactionsProfile, regAlg):
		pass


class RandomFitness(FitnessAlg):
	def calculate(player, interactionsProfile, regAlg):
		return 0.0


class SimulationsOptimalFitness(FitnessAlg):
	def calculate(player, interactionsProfile, regAlg):
		predictedState = PlayerState(player.getCurrState());

		abilityInc = predictedState.characteristics.ability - player.getCurrState().characteristics.ability;
		return abilityInc;

class WeightedFitness(FitnessAlg):
	def __init__(self, modelWeights):
		self.modelWeights = modelWeights;

	def calculate(player, interactionsProfile, regAlg):
		predictedModel = regAlg.predict(interactionsProfile, player)
		return self.modelWeights.ability*(predictedModel.characteristics.ability) + self.modelWeights.engagement*predictedModel.characteristics.engagement; #ability must be normalized to [0,1]