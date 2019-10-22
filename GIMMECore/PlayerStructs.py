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
	def __init__(self, numCells=1, maxAmountOfStoredProfilesPerCell=30):
		self.numCells = numCells;
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;
		self.cells = [[]]

	def pushToGrid(self, playerState):
		dimSpan = cbrt(numCells-1);
		currCellInd = (dimSpan * dimSpan * floor(dimSpan * model.profile.K_cl) + dimSpan * floor(dimSpan * model.profile.K_cp) + floor(dimSpan* model.profile.K_i))
		
		currCell = self.cells[currCellInd]
		currCell.append(playerState)
		cellsSize = len(cells[currCellInd])
		if (cellsSize > maxAmountOfStoredProfilesPerCell):
			currCell = currCell[maxAmountOfStoredProfilesPerCell:]

		self.cells[currCellInd] = currCell