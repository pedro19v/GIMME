import copy
from abc import ABC, abstractmethod
from AlgDefStructs.RegressionAlg import * 

class FitnessAlg(ABC):
	@abstractmethod
	def calculate(self, playerModelBridge, predictedState):
		pass

class WeightedFitness(FitnessAlg):
	def __init__(self, stateWeights):
		self.stateWeights = stateWeights;

	def calculate(self, playerModelBridge, predictedState):
		return self.stateWeights.ability*predictedState.characteristics.ability + self.stateWeights.engagement*predictedState.characteristics.engagement #ability must be normalized to [0,1]