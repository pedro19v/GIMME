from abc import ABC, abstractmethod
import copy
from ..PlayerStructs import *
import json

class GridTrimAlg(ABC):

	def __init__(self):
		pass

	@abstractmethod
	def toRemoveList(self, pastModelIncs):
		pass


# ---------------------- KNNRegression stuff ---------------------------
class AgeSortGridTrimAlg(GridTrimAlg):

	def __init__(self, maxNumModelElements):
		super().__init__()
		self.maxNumModelElements = maxNumModelElements

	def creationTimeSort(self, elem):
		return elem.creationTime

	def toRemoveList(self, pastModelIncs):
		pastModelIncsCopy = pastModelIncs.copy()
		pastModelIncsCopy = sorted(pastModelIncsCopy, key=self.creationTimeSort)
		return pastModelIncsCopy[:-self.maxNumModelElements]


class QualitySortGridTrimAlg(GridTrimAlg):

	def __init__(self, maxNumModelElements, qualityWeights = None, accStateResidue = None):
		super().__init__()
		self.maxNumModelElements = maxNumModelElements
		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights==None else qualityWeights
		self.accStateResidue = False if accStateResidue == None else accStateResidue

		self.ageTrimmer = AgeSortGridTrimAlg(maxNumModelElements)

	def considerStateResidue(self, accStateResidue):
		self.accStateResidue = accStateResidue

	def stateTypeFilter(self, element):
		return element.stateType == 0

	def qSort(self, elem):
		return elem.quality
	def calcQuality(self, state):
		return self.qualityWeights.ability*state.characteristics.ability + self.qualityWeights.engagement*state.characteristics.engagement
	
	def toRemoveList(self, pastModelIncs):
		pastModelIncsCopy = pastModelIncs.copy()

		bootstrapResidue = []
		toRemoveList = []

		if(self.accStateResidue):
			bootstrapResidue = list(filter(self.stateTypeFilter, pastModelIncsCopy))
			# check for bootstrap residue and trim on age
			toRemoveList.extend(self.ageTrimmer.toRemoveList(bootstrapResidue))
			# the rest is trimmed on quality
			pastModelIncsCopy = list(set(pastModelIncsCopy) - set(bootstrapResidue))

		for modelInc in pastModelIncsCopy:
			if(modelInc.quality == -1):
				modelInc.quality = self.calcQuality(modelInc)
		pastModelIncsCopy = sorted(pastModelIncsCopy, key=self.qSort)
		toRemoveList.extend(pastModelIncsCopy[:-self.maxNumModelElements])
		
		return toRemoveList

class QualitySoftMaxGridTrimAlg(GridTrimAlg):

	def __init__(self, qualityWeights = None):
		super().__init__()

	def toRemoveList(self, pastModelIncs):
		pass
		