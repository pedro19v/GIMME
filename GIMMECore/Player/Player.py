import numpy
from PlayerStructs import *

class Player (object):
	# private:
	def saveIncreases(stateIncreases):
		self.currModelIncreases = stateIncreases;
		self.pastModelIncreasesGrid.pushToGrid(stateIncreases);

	# public:
	def __init__(self, id, name, numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell, utilities):
		
		self.currState = PlayerState()

		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = PlayerStateGrid(numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell)

		# Adaptation part
		self.numPastModelIncreasesCells = numPastModelIncreasesCells;
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;

		self.utilities = utilities
		
		# for displaying in charts
		self.currModelIncreases = PlayerState(); 


	def reset(self, numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell):
		self.currState = PlayerState()
		self.pastModelIncreasesGrid = PlayerStateGrid(numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell)

	def getPastModelIncreases(self):
		return self.pastModelIncreasesGrid.getAllStates()
	def getCurrState(self):
		return self.currState

	def setCharacteristics(self, characteristics):
		self.currState.characteristics = characteristics

	def setCurrProfile(self, profile):
		self.currState.profile = profile;

	def getId(self):
		return self.id;

	def getName(self):
		return self.name;

	def getCurrProfile(self):
		return self.currState.profile