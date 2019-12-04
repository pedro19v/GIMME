import numpy
import math
import time
from collections import namedtuple
from InteractionsProfile import InteractionsProfile

import json


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
		self.tailoredTaskId = -1

	def reset(self):
		self.characteristics.reset()
		self.profile.reset()
		self.dist = -1
		self.groupId = -1


class PlayerStateGrid(object):
	def __init__(self, numCells=1, maxProfilesPerCell=30,  cells=None):
		self.maxProfilesPerCell = maxProfilesPerCell

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
		cpPadding = math.ceil(playerState.profile.K_cp * self.dimSpan) - 1
		iPadding = math.ceil(playerState.profile.K_i * self.dimSpan) - 1
		mhPadding = math.ceil(playerState.profile.K_mh * self.dimSpan) - 1
		eaPadding = math.ceil(playerState.profile.K_ea * self.dimSpan) - 1

		currCellInd = (self.dimSpan**3)*cpPadding + (self.dimSpan**2)*iPadding + self.dimSpan*mhPadding + eaPadding
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
