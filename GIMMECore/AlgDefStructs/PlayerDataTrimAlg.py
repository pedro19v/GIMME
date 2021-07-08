from abc import ABC, abstractmethod
import copy
from ..PlayerStructs import *
import json

class PlayerDataTrimAlg(ABC):

	def __init__(self):
		pass

	@abstractmethod
	def trimmedList(self, pastModelIncs):
		pass


# ---------------------- KNNRegression stuff ---------------------------
class AgeSortPlayerDataTrimAlg(PlayerDataTrimAlg):

	def __init__(self, maxNumModelElements):
		super().__init__()
		self.maxNumModelElements = maxNumModelElements

	def creationTimeSort(self, elem):
		return elem.creationTime

	def trimmedList(self, pastModelIncs):

		if(len(pastModelIncs) < self.maxNumModelElements):
			return [pastModelIncs, []]

		pastModelIncsSorted = sorted(pastModelIncs, key=self.creationTimeSort)
		removedI = pastModelIncs.index(pastModelIncsSorted[self.maxNumModelElements - 1])
		pastModelIncs.pop(removedI)
		return [pastModelIncs, [removedI]]


class QualitySortPlayerDataTrimAlg(PlayerDataTrimAlg):

	def __init__(self, maxNumModelElements, qualityWeights = None, accStateResidue = None):
		super().__init__()
		self.maxNumModelElements = maxNumModelElements
		self.qualityWeights = PlayerCharacteristics(ability = 0.5, engagement = 0.5) if qualityWeights==None else qualityWeights
		self.accStateResidue = False if accStateResidue == None else accStateResidue

	def considerStateResidue(self, accStateResidue):
		self.accStateResidue = accStateResidue

	def stateTypeFilter(self, element):
		return element.stateType == 0

	def qSort(self, elem):
		return elem.quality

	def calcQuality(self, state):
		total = self.qualityWeights.ability*state.characteristics.ability + self.qualityWeights.engagement*state.characteristics.engagement
		return total

	def trimmedList(self, pastModelIncs):

		for modelInc in pastModelIncs:
			if(modelInc.quality == -1):
				modelInc.quality = self.calcQuality(modelInc)
				if(self.accStateResidue):
					modelInc.quality += modelInc.stateType


		if(len(pastModelIncs) <= self.maxNumModelElements):
			return [pastModelIncs, []]

		pastModelIncsSorted = sorted(pastModelIncs, key=self.qSort)
		removedI = pastModelIncs.index(pastModelIncsSorted[0])
		pastModelIncs.pop(removedI)
		return [pastModelIncs, [removedI]]


# class QualitySoftMaxPlayerDataTrimAlg(PlayerDataTrimAlg):

# 	def __init__(self, qualityWeights = None):
# 		super().__init__()

# 	def trimmedList(self, pastModelIncs):
# 		pass
		