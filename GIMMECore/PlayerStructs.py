import numpy
import math
import time
from collections import namedtuple
from AuxStructs.InteractionsProfile import InteractionsProfile

import json

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
		self.creationTime = time.time()
	def reset(self):
		self.profile.reset()
		self.characteristics.reset()
		self.dist = 0

class PlayerStateGrid(object):
	def __init__(self, numCells=1, maxAmountOfStoredProfilesPerCell=30,  cells=None):
		self.numCells = numCells
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell
		self.initialCells = cells
		if(self.initialCells == None):
			self.cells = [[]*self.maxAmountOfStoredProfilesPerCell]*self.numCells
		else:
			self.cells = cells

	def reset(self):
		if(self.initialCells == None):
			self.cells = [[]*self.maxAmountOfStoredProfilesPerCell]*self.numCells
		else:
			self.cells = cells

	def pushToGrid(self, playerState):
		dimSpan = (self.numCells-1)**(1/float(4)) #root 4
		currCellInd = (dimSpan *dimSpan*dimSpan * math.floor(dimSpan * playerState.profile.K_cp) + dimSpan*dimSpan*  math.floor(dimSpan * playerState.profile.K_i) + dimSpan * math.floor(dimSpan* playerState.profile.K_mh) + math.floor(dimSpan* playerState.profile.K_pa))
		currCellInd = int(currCellInd)
		currCell = self.cells[currCellInd]
		currCell.append(playerState)
		
		cellsSize = len(self.cells[currCellInd])
		if (cellsSize > self.maxAmountOfStoredProfilesPerCell):
			currCell = currCell[-self.maxAmountOfStoredProfilesPerCell:]

		self.cells[currCellInd] = currCell
		# print(json.dumps(self.cells, default=lambda o: o.__dict__, sort_keys=True))

	def getAllStates(self):
		# serialize multi into single dimensional array
		allStates = []
		for cell in self.cells:
			for state in cell:
				allStates.append(state) 
		return allStates
