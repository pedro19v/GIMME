import math
import time
import copy
import json
from .InteractionsProfile import InteractionsProfile



class PlayerCharacteristics(object):
	def __init__(self, ability = None, engagement = None):
		self.ability = 0 if ability==None else ability
		self.engagement = 0 if engagement==None else engagement
	def reset(self):
		self.ability = 0
		self.engagement = 0
		return self

class PlayerState(object):
	def __init__(self, stateType = None, profile = None, characteristics = None, dist = None, quality = None):
		self.creationTime = time.time()
		
		self.stateType = 1 if stateType == None else stateType
		self.profile = InteractionsProfile() if profile == None else profile
		self.characteristics = PlayerCharacteristics() if characteristics == None else characteristics
		self.dist = -1 if dist == None else dist
		self.quality = -1 if quality == None else quality

		self.groupId = -1
		self.adaptedTaskId = -1

	def reset(self):
		self.characteristics.reset()
		self.profile.reset()
		self.creationTime = time.time()
		self.stateType = 1
		self.quality = -1
		self.dist = -1
		self.groupId = -1
		self.adaptedTaskId = -1
		return self


class PlayerStateGrid(object):
	def __init__(self, interactionsProfileTemplate, gridTrimAlg, numCells = None, cells = None):
		self.interactionsProfileTemplate = interactionsProfileTemplate
		self.gridTrimAlg = gridTrimAlg

		numCells = 1 if numCells == None else numCells
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

		if(currCellInd==1):
			breakpoint()
		# print(playerState.profile.dimensions)

		currCell = self.cells[currCellInd]
		
		currCell.append(playerState)
		self.serializedCells.append(playerState)
		self.numCellStates = self.numCellStates + 1
		


		# actionTime = len(currCell)> 10
		# if(actionTime):
		# 	print("serialezCells: "+json.dumps(self.serializedCells, default=lambda o: o.__dict__, sort_keys=True))

		statesToDelete = self.gridTrimAlg.toRemoveList(self.cells[currCellInd])
		
		# if(actionTime):
		# 	print("statesToDelete: "+json.dumps(statesToDelete, default=lambda o: o.__dict__, sort_keys=True))
		
		self.serializedCells = list(set(self.serializedCells) - set(statesToDelete))
		self.numCellStates = self.numCellStates - len(statesToDelete)
		currCell = list(set(currCell) - set(statesToDelete))

		# if(actionTime):
		# 	print("serializedCells2: "+json.dumps(self.serializedCells, default=lambda o: o.__dict__, sort_keys=True))
		
		# if(actionTime):
		# 	breakpoint()


		self.cells[currCellInd] = currCell


	def getAllStates(self):
		# serialize multi into single dimensional array
		return self.serializedCells

	def getNumStates(self):
		return self.numCellStates
