import copy
from abc import ABC, abstractmethod
from AlgDefStructs.RegressionAlg import * 

class FitnessAlg(ABC):
	@abstractmethod
	def calculate(self, playerModelBridge, playerId, interactionsProfile, regAlg):
		pass


class RandomFitness(FitnessAlg):
	def calculate(self, playerModelBridge, playerId, interactionsProfile, regAlg):
		return 0.0


class SimulationsOptimalFitness(FitnessAlg):
	def calculate(self, playerModelBridge, playerId, interactionsProfile, regAlg):
		predictedState = copy.deepcopy(playerModelBridge.getCurrState(playerId))
		abilityInc = predictedState.characteristics.ability - playerModelBridge.getCurrState(playerId).characteristics.ability
		return abilityInc;

class WeightedFitness(FitnessAlg):
	def __init__(self, stateWeights):
		self.stateWeights = stateWeights;

	def calculate(self, playerModelBridge, playerId, interactionsProfile, regAlg):
		predictedState = regAlg.predict(interactionsProfile, playerModelBridge, playerId)
		return self.stateWeights.ability*(predictedState.characteristics.ability) + self.stateWeights.engagement*predictedState.characteristics.engagement #ability must be normalized to [0,1]