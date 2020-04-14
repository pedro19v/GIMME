import math
import time
import copy
import json
from .InteractionsProfile import InteractionsProfile



class PlayerCharacteristics(object):
	def __init__(self, ability=0, engagement=0):
		self.ability = ability
		self.engagement = engagement
	def reset(self):
		self.ability = 0
		self.engagement = 0

class PlayerState(object):
	def __init__(self, creationTime = time.time(), profile = InteractionsProfile(), characteristics = PlayerCharacteristics(), dist = -1):
		self.characteristics = characteristics
		self.creationTime = creationTime
		self.profile = profile
		self.dist = dist
		self.groupId = -1
		self.adaptedTaskId = -1

	def reset(self):
		self.characteristics.reset()
		self.profile.reset()
		self.dist = -1
		self.groupId = -1


class PlayerStateGrid(object):
	def __init__(self, interactionsProfileTemplate, numCells=1, maxProfilesPerCell=30,  cells=None):
		self.maxProfilesPerCell = maxProfilesPerCell
		self.interactionsProfileTemplate = interactionsProfileTemplate

		self.dimSpan = math.ceil(numCells**(1.0/float(4))) #floor of root 4
		self.numCells = self.dimSpan**4
		
		self.initialCells = cells
		if(self.initialCells == None):
			self.cells = [[] for i in range(self.numCells)]
			self.serializedCells = []
		else:
			self.cells = cells
			self.serializedCells = []
			for cell in self.cells:
				for state in cell:
					self.serializedCells.append(state) 

	def reset(self):
		if(self.initialCells == None):
			self.cells = [[] for i in range(self.numCells)]
			self.serializedCells = []
		else:
			self.cells = cells
			self.serializedCells = []
			for cell in self.cells:
				for state in cell:
					self.serializedCells.append(state) 

	def pushToGrid(self, playerState):
		padding = self.interactionsProfileTemplate.generateCopy()
		padding.reset()
		currCellInd = 0
		paddingKeys = list(padding.dimensions.keys())
		for key in padding.dimensions:
			currDim = padding.dimensions[key]
			currDim = math.ceil(playerState.profile.dimensions[key] * self.dimSpan) - 1
			if(currDim < 0):
				currDim=0
			currCellInd += (self.dimSpan**paddingKeys.index(key))*currDim
			padding.dimensions[key] = currDim


		# print(json.dumps(len(self.cells[0]), default=lambda o: o.__dict__, sort_keys=True))
		# currCellInd = (self.dimSpan**3)*cpPadding + (self.dimSpan**2)*iPadding + self.dimSpan*mhPadding + eaPadding
		currCell = self.cells[currCellInd]
		
		currCell.append(playerState)
		self.serializedCells.append(playerState)
		
		cellsSize = len(self.cells[currCellInd])
		if (cellsSize > self.maxProfilesPerCell):
			stateToDelete = currCell[0]
			self.serializedCells.remove(stateToDelete)
			currCell = currCell[-self.maxProfilesPerCell:]

		self.cells[currCellInd] = currCell

	def getAllStates(self):
		# serialize multi into single dimensional array
		return self.serializedCells
