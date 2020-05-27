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
		return self

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
		return self


class PlayerStateGrid(object):
	def __init__(self, interactionsProfileTemplate, numCells=1, maxProfilesPerCell=30,  cells=None):
		self.maxProfilesPerCell = maxProfilesPerCell
		self.interactionsProfileTemplate = interactionsProfileTemplate

		self.dimSpan = math.ceil(numCells**(1.0/float(4))) #floor of root 4
		self.numCells = self.dimSpan**4
		
		self.numCellStates = 0

		self.initialCells = cells
		if(self.initialCells == None):
			self.cells = [[] for i in range(self.numCells)]
			self.serializedCells = []
			self.numCellStates = 0
		else:
			self.cells = cells
			self.serializedCells = []
			self.numCellStates = 0
			for cell in self.cells:
				for state in cell:
					self.serializedCells.append(state) 
					self.numCellStates = self.numCellStates + 1

	def reset(self):
		self.numCellStates = 0
		if(self.initialCells == None):
			self.cells = [[] for i in range(self.numCells)]
			self.serializedCells = []
			self.numCellStates = 0
		else:
			self.cells = cells
			self.serializedCells = []
			self.numCellStates = 0
			for cell in self.cells:
				for state in cell:
					self.serializedCells.append(state) 
					self.numCellStates = self.numCellStates + 1
		return self

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

		currCell = self.cells[currCellInd]
		
		currCell.append(playerState)
		self.serializedCells.append(playerState)
		self.numCellStates = self.numCellStates + 1
		
		cellsSize = len(self.cells[currCellInd])
		if (cellsSize > self.maxProfilesPerCell):
			stateToDelete = currCell[0]
			self.serializedCells.remove(stateToDelete)
			self.numCellStates = self.numCellStates - 1
			currCell = currCell[-self.maxProfilesPerCell:]

		self.cells[currCellInd] = currCell

	def getAllStates(self):
		# serialize multi into single dimensional array
		return self.serializedCells

	def getNumStates(self):
		return self.numCellStates
