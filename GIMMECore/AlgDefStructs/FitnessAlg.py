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
	def __init__(self, simulationFunc, stateWeights):
		self.stateWeights = stateWeights
		self.simulationFunc = simulationFunc
		self.currIteration = 0

	def updateCurrIteration(self, newCurrIteration):
		self.currIteration = newCurrIteration

	def calculate(self, playerModelBridge, playerId, interactionsProfile, regAlg):
		currState = copy.deepcopy(playerModelBridge.getPlayerCurrState(playerId))
		newState = self.simulationFunc(copy.deepcopy(currState), playerModelBridge, playerId, interactionsProfile, self.currIteration)
		# newState.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
		return self.stateWeights.ability*newState.characteristics.ability + self.stateWeights.engagement*newState.characteristics.engagement

class WeightedFitness(FitnessAlg):
	def __init__(self, stateWeights):
		self.stateWeights = stateWeights;

	def calculate(self, playerModelBridge, playerId, interactionsProfile, regAlg):
		predictedState = regAlg.predict(interactionsProfile, playerModelBridge, playerId)
		return self.stateWeights.ability*predictedState.characteristics.ability + self.stateWeights.engagement*predictedState.characteristics.engagement #ability must be normalized to [0,1]