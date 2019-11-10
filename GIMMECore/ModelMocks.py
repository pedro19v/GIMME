import random
from PlayerStructs import *

class PlayerModelMock(object):
	def __init__(self, id, name, currState, pastModelIncreasesGrid, currModelIncreases, personality, numIterationsPerRun):
		self.currState = currState

		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = pastModelIncreasesGrid

		self.personality = personality

		# for simulations
		# self.inherentPreference = None
		self.baseLearningRate = None
		self.iterationReactions = None


class TaskModelMock(object):
	def __init__(self, id, description, minRequiredAbility, profile, difficultyWeight, profileWeight):
		
		self.id = id

		self.description = description
		self.minRequiredAbility = minRequiredAbility
		self.profile = profile
		self.difficultyWeight = difficultyWeight
		self.profileWeight = profileWeight
