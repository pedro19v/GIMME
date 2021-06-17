from abc import ABC, abstractmethod
import copy
from ..PlayerStructs import *
import json

class GridTrimAlg(ABC):

	def __init__(self):
		pass

	@abstractmethod
	def trimmedList(self, pastModelIncs):
		pass


# ---------------------- KNNRegression stuff ---------------------------
class AgeSortGridTrimAlg(GridTrimAlg):

	def __init__(self, maxNumModelElements):
		super().__init__()
		self.maxNumModelElements = maxNumModelElements

	def creationTimeSort(self, elem):
		return elem.creationTime

	def trimmedList(self, pastModelIncs):

		if(len(pastModelIncs) < self.maxNumModelElements):
			return pastModelIncs

		pastModelIncs = sorted(pastModelIncs, key=self.creationTimeSort)
		return [pastModelIncs[-self.maxNumModelElements:],pastModelIncs[:-self.maxNumModelElements]]


class QualitySortGridTrimAlg(GridTrimAlg):

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
		if(self.accStateResidue):
			total += state.stateType
		return total

	def trimmedList(self, pastModelIncs):

		for modelInc in pastModelIncs:
			if(modelInc.quality == -1):
				modelInc.quality = self.calcQuality(modelInc)


		if(len(pastModelIncs) < self.maxNumModelElements):
			return pastModelIncs

		pastModelIncs = sorted(pastModelIncs, key=self.qSort)
		return [pastModelIncs[-self.maxNumModelElements:],pastModelIncs[:-self.maxNumModelElements]]

# class QualitySoftMaxGridTrimAlg(GridTrimAlg):

# 	def __init__(self, qualityWeights = None):
# 		super().__init__()

# 	def trimmedList(self, pastModelIncs):
# 		pass
		