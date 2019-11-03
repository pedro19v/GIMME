import numpy
import math
from collections import namedtuple
from AuxStructs.InteractionsProfile import InteractionsProfile

class PlayerCharacteristics(object):
	def __init__(self, ability=0, engagement=0):
		self.ability = ability
		self.engagement = engagement
	def reset(self):
		self.ability = 0
		self.engagement = 0

class PlayerState(object):
	def __init__(self, profile = InteractionsProfile(), characteristics = PlayerCharacteristics(), dist = 0):
		self.profile = profile
		self.characteristics = characteristics
		self.dist = dist
	def reset(self):
		self.profile = InteractionsProfile()
		self.characteristics = PlayerCharacteristics()
		self.dist = 0

class PlayerStateGrid(object):
	def __init__(self, cells=None, numCells=1, maxAmountOfStoredProfilesPerCell=30):
		self.numCells = numCells
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell
		if(cells == None):
			self.cells = [[]*maxAmountOfStoredProfilesPerCell]*numCells
		else:
			self.cells = cells
		print(cells)

	def reset(self):
		self.cells = [[]*maxAmountOfStoredProfilesPerCell]*numCells

	def pushToGrid(self, playerState):
		dimSpan = numpy.cbrt(self.numCells-1);
		currCellInd = (dimSpan * dimSpan * math.floor(dimSpan * playerState.profile.K_cl) + dimSpan * math.floor(dimSpan * playerState.profile.K_cp) + math.floor(dimSpan* playerState.profile.K_i))
		currCellInd = int(currCellInd)
		currCell = self.cells[currCellInd]
		currCell.append(playerState)
		cellsSize = len(self.cells[currCellInd])
		if (cellsSize > self.maxAmountOfStoredProfilesPerCell):
			currCell = currCell[self.maxAmountOfStoredProfilesPerCell:]

		self.cells[currCellInd] = currCell

	def getAllStates(self):
		# serialize multi into single dimensional array
		allStates = []
		for cell in self.cells:
			for state in cell:
				allStates.append(state) 
		return allStates
