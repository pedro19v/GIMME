import numpy
from PlayerStructs import *

class PlayerModelMock(object):
	def __init__(self, id, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		self.currState = currState

		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = pastModelIncreasesGrid

		self.personality = personality; 
		
		# for displaying in charts
		self.currModelIncreases = currModelIncreases; 

class TaskModelMock(object):
	def __init__(self, id, description, minRequiredAbility, profile, difficultyWeight, profileWeight):
		
		self.id = id

		self.description = description
		self.minRequiredAbility = minRequiredAbility
		self.profile = profile
		self.difficultyWeight = difficultyWeight
		self.profileWeight = profileWeight
		self.profile = profile
