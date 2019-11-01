import numpy
import math
from collections import namedtuple
from AuxStructs.InteractionsProfile import InteractionsProfile

class PlayerCharacteristics(object):
	def __init__(self, ability=0, engagement=0):
		self.ability = ability
		self.engagement = engagement

class PlayerState(object):
	def __init__(self, profile = InteractionsProfile(), characteristics = PlayerCharacteristics(), dist = 0):
		self.profile = profile
		self.characteristics = characteristics
		self.dist = dist

class PlayerStateGrid(object):
	def __init__(self, cells=[], numCells=1, maxAmountOfStoredProfilesPerCell=30):
		self.numCells = numCells
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell
		self.cells = [[]*maxAmountOfStoredProfilesPerCell]*numCells
		print(cells)

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

	def getAllCells(self):
		allCells = []
		for cell in self.cells:
			for item in cell:
				allCells.append(cell) 
		return allCells