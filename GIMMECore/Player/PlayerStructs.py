import numpy
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
	def __init__(self):
		pass

	def __init__(self, numCells, maxAmountOfStoredProfilesPerCell):
	# private:
		self.numCells = numCells;
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;
		self.cells =  numpy.empty(numCells)

	def pushToGrid(self, playerState):
		dimSpan = cbrt(numCells-1);
		currCellInd = (dimSpan * dimSpan * floor(dimSpan * model.profile.K_cl) + dimSpan * floor(dimSpan * model.profile.K_cp) + floor(dimSpan* model.profile.K_i));
		
		currCell = self.cells[currCellInd];
		currCell = numpy.append(currCell, playerState);
		cellsSize = len(cells[currCellInd]);
		if (cellsSize > maxAmountOfStoredProfilesPerCell):
			currCell = currCell[1:]

		self.cells[currCellInd] = currCell

	def getAllStates(self):
		allCells = numpy.empty(0);
		for i in range(len(self.cells)):
			currCell = self.cells[i]
			allCells = numpy.append(allCells, currCell)
		
		return allCells;
	# public: