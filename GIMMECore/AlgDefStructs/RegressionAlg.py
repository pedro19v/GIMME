import copy
import json
import pandas as pd

from abc import ABC, abstractmethod

from GIMMECore.ModelBridge.TaskModelBridge import TaskModelBridge
from ..PlayerStructs import *

from sklearn import linear_model, neighbors

class RegressionAlg(ABC):

	def __init__(self, playerModelBridge):
		self.playerModelBridge = playerModelBridge

		self.completionPerc = 0.0

	@abstractmethod
	def predict(self, profile, playerId):
		pass

	def isTabular(self):
		return False

	# instrumentation
	def getCompPercentage(self):
		return self.completionPerc


# ---------------------- KNNRegression ---------------------------
class KNNRegression(RegressionAlg):

	def __init__(self, playerModelBridge, numberOfNNs):
		super().__init__(playerModelBridge)
		self.numberOfNNs = numberOfNNs

	def distSort(self, elem):
		return elem.dist

	def creationTimeSort(self, elem):
		return elem.creationTime

	def predict(self, profile, playerId):
		# import time
		# startTime = time.time()

		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStates().copy()
		pastModelIncsSize = len(pastModelIncs)

		predictedState = PlayerState(profile = profile, characteristics = PlayerCharacteristics())
	
		for modelInc in pastModelIncs:
			modelInc.dist = profile.sqrDistanceBetween(modelInc.profile)

		pastModelIncs = sorted(pastModelIncs, key=self.distSort)

		numberOfIterations = min(self.numberOfNNs, len(pastModelIncs))
		pastModelIncs = pastModelIncs[:numberOfIterations]

		triangularNumberOfIt = sum(range(numberOfIterations + 1))
		for i in range(numberOfIterations):

			self.completionPerc = i/ numberOfIterations

			currState = pastModelIncs[i]
			pastCharacteristics = currState.characteristics
			ratio = (numberOfIterations - i)/triangularNumberOfIt

			predictedState.characteristics.ability += pastCharacteristics.ability * ratio
			predictedState.characteristics.engagement += pastCharacteristics.engagement * ratio

		# executionTime = (time.time() - startTime)
		# print('Execution time in seconds: ' + str(executionTime))
		
		return predictedState

# ---------------------- KNNRegressionSKLearn ---------------------------
class KNNRegressionSKLearn(RegressionAlg):

	def __init__(self, playerModelBridge, numberOfNNs):
		super().__init__(playerModelBridge)
		self.numberOfNNs = numberOfNNs


	def predict(self, profile, playerId):
		# import time
		# startTime = time.time()

		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStatesFlatten()

		lenPMI = len(pastModelIncs['profiles'])
		
		numberOfNNs = self.numberOfNNs
		if(lenPMI < self.numberOfNNs):
			if(lenPMI==0):
				return PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = 0.5, engagement = 0.5))
			numberOfNNs = lenPMI

		profData = profile.flattened()
		prevProfs = pastModelIncs['profiles']
		

		self.regrAb = neighbors.KNeighborsRegressor(numberOfNNs, weights="distance")
		self.regrAb.fit(prevProfs, pastModelIncs['abilities'])
		predAbilityInc = self.regrAb.predict([profData])[0]

		self.regrEng = neighbors.KNeighborsRegressor(numberOfNNs, weights="distance")
		self.regrEng.fit(prevProfs, pastModelIncs['engagements'])
		predEngagement = self.regrEng.predict([profData])[0]

		predState = PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = predAbilityInc, engagement = predEngagement))
		

		self.completionPerc = 1.0

		# executionTime = (time.time() - startTime)
		# print('Execution time in seconds: ' + str(executionTime))

		return predState

# ---------------------- LinearRegressionSKLearn ---------------------------
class LinearRegressionSKLearn(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		
		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStatesFlatten()

		if(len(pastModelIncs['profiles'])==0):
			return PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = 0.5, engagement = 0.5))

		profData = profile.flattened()

		prevProfs = pastModelIncs['profiles']

		regr = linear_model.LinearRegression() 
		regr.fit(prevProfs, pastModelIncs['abilities'])
		predAbilityInc = regr.predict([profData])[0]

		regr.fit(prevProfs, pastModelIncs['engagements'])
		predEngagement = regr.predict([profData])[0]

		predState = PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = predAbilityInc, engagement = predEngagement))
		
		self.completionPerc = 1.0

		return predState

# ---------------------- SVMRegressionSKLearn ---------------------------
class SVMRegressionSKLearn(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		
		pastModelIncs = self.playerModelBridge.getPlayerStatesDataFrame(playerId).getAllStatesFlatten()

		if(len(pastModelIncs['profiles'])==0):
			return PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = 0.5, engagement = 0.5))

		profData = profile.flattened()

		prevProfs = pastModelIncs['profiles']

		regr = svm.SVR()
		regr.fit(prevProfs, pastModelIncs['abilities'])
		predAbility = regr.predict([profData])[0]

		regr.fit(prevProfs, pastModelIncs['engagements'])
		predEngagement = regr.predict([profData])[0]

		predState = PlayerState(profile = profile, characteristics = PlayerCharacteristics(ability = predAbility, engagement = predEngagement))
		
		self.completionPerc = 1.0

		return predState

# ---------------------- DecisionTreesRegression ---------------------------
class DecisionTreesRegression(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass


# ---------------------- NeuralNetworkRegression ---------------------------
class NeuralNetworkRegression(RegressionAlg):

	def __init__(self, playerModelBridge):
		super().__init__(playerModelBridge)

	def predict(self, profile, playerId):
		pass


# ---------------------- Tabular Agent Synergy Method -------------------------------------
class TabularAgentSynergies(RegressionAlg):

	def __init__(self, playerModelBridge, taskModelBridge):
		super().__init__(playerModelBridge)
		
		self.taskModelBridge = taskModelBridge
		tempTable = pd.read_csv('synergyTable.txt', sep=",") 
		self.synergyTable = tempTable.pivot_table(values='synergy', index='agent_1', columns='agent_2') 

		# tempTable = pd.read_csv('taskTable.txt', sep=',')
		# self.taskTable = tempTable.pivot_table(values='synergy', index='taskId', columns='agent')


	def isTabular(self):
		return True

	def predict(self, profile, playerId):
		firstPlayerPreferencesInString = '('
		for dim in profile.dimensions:
			firstPlayerPreferencesInString += str(round(profile.dimensions[dim]))
		firstPlayerPreferencesInString += ')'

		secondPlayerPreferences = self.playerModelBridge.getPlayerPreferencesEst(playerId)
		secondPlayerPreferenceInString = '('
		for dim in secondPlayerPreferences.dimensions:
			secondPlayerPreferenceInString += str(round(secondPlayerPreferences.dimensions[dim]))
		
		secondPlayerPreferenceInString += ')'

		return self.synergyTable[secondPlayerPreferenceInString][firstPlayerPreferencesInString]

	# either this, or find here the best task
	def predictTasks(self, taskId, playerId):
		playerPreferences = self.playerModelBridge.getPlayerPreferencesEst(playerId)
		playerPreferenceInString = '('
		for dim in playerPreferences.dimensions:
			playerPreferenceInString += str(round(playerPreferences.dimensions[dim]))
		playerPreferenceInString += ')'

		taskProfile = self.taskModelBridge.getTaskInteractionsProfile(taskId)
		taskProfileInString = '('
		for dim in taskProfile.dimensions:
			taskProfileInString += str(round(taskProfile.dimensions[dim]))
		taskProfileInString += ')'

		return self.taskTable[playerPreferenceInString][taskProfileInString]



# X = pd.read_csv('synergyTable.txt', sep=",") 
# >>> X.pivot_table(values='synergy', index='agent1', columns='agent2')
# agent2  (00)  (01)  (10)  (11)
# agent1
# (00)       1     0     0     0
# (01)       0     1     0     0
# (10)       0     0     1     0
# (11)       0     0     0     1
# >>> dX = X.pivot_table(values='synergy', index='agent1', columns='agent2')
# >>> dX
# agent2  (00)  (01)  (10)  (11)
# agent1
# (00)       0     0     0     0
# (01)       0     0     0     0
# (10)       0     0     0     0
# (11)       0     0     0     0
# >>> dX['(00)']
# agent1
# (00)    0
# (01)    0
# (10)    0
# (11)    0