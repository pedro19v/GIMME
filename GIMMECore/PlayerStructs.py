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
	def __init__(self, creationTime, profile = InteractionsProfile(), characteristics = PlayerCharacteristics(), dist = 0):
		self.profile = profile
		self.characteristics = characteristics
		self.dist = dist
		self.creationTime = creationTime
	def reset(self):
		self.profile.reset()
		self.characteristics.reset()
		self.dist = 0

class PlayerStateGrid(object):
	def __init__(self, numCells=1, maxAmountOfStoredProfilesPerCell=30,  cells=None):
		self.maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell

		self.dimSpan = math.ceil(numCells**(1.0/float(4))) #floor of root 4
		self.numCells = self.dimSpan**4
		
		self.initialCells = cells
		if(self.initialCells == None):
			self.cells = [[]*self.maxAmountOfStoredProfilesPerCell]*self.numCells
			# self.cells = numpy.ndarray(shape=(self.numCells,self.maxAmountOfStoredProfilesPerCell))
		else:
			self.cells = cells

	def reset(self):
		if(self.initialCells == None):
			self.cells = [[]*self.maxAmountOfStoredProfilesPerCell]*self.numCells
			# self.cells = numpy.ndarray(shape=(self.numCells,self.maxAmountOfStoredProfilesPerCell))
		else:
			self.cells = cells

	def pushToGrid(self, playerState):


		cpPadding = math.ceil(playerState.profile.K_cp * self.dimSpan) - 1
		iPadding = math.ceil(playerState.profile.K_i * self.dimSpan) - 1
		mhPadding = math.ceil(playerState.profile.K_mh * self.dimSpan) - 1
		paPadding = math.ceil(playerState.profile.K_pa * self.dimSpan) - 1

		currCellInd = (self.dimSpan**3)*cpPadding + (self.dimSpan**2)*iPadding + self.dimSpan*mhPadding + paPadding
		currCell = self.cells[currCellInd]
		
		currCell.append(playerState)
		
		cellsSize = len(self.cells[currCellInd])
		if (cellsSize > (self.maxAmountOfStoredProfilesPerCell - 1)):
			currCell = currCell[-self.maxAmountOfStoredProfilesPerCell:]
		self.cells[currCellInd] = currCell

	def getAllStates(self):
		# serialize multi into single dimensional array
		allStates = []
		for cell in self.cells:
			for state in cell:
				allStates.append(state) 
		return allStates
