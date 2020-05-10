import math
import copy

class InteractionsProfile(object):

	def __init__(self, dimensions = {}):
		self.dimensions = dimensions

	def reset(self):
		for key in self.dimensions:
			self.dimensions[key] = 0

	def generateCopy(self):
		keys = list(self.dimensions.keys())
		newVar = type(self)(copy.copy(self.dimensions))
		for key in keys:
			newVar.dimensions[key] = self.dimensions[key]
		return newVar

	def normalize(self):
		if(len(self.dimensions)>2):
			total = 0
			for key in self.dimensions:
				total += self.dimensions[key]
			if(total==0):
				for key in self.dimensions:
					self.dimensions[key] = 0.25
			else:
				for key in self.dimensions:
					self.dimensions[key] = self.dimensions[key]/total

	

	def sqrDistanceBetween(self, profileToTest):
		cost = self.generateCopy()
		cost.reset()

		if(len(cost.dimensions) != len(profileToTest.dimensions)):
			print("[ERROR] Could not compute distance between profiles in different sized spaces. Execution aborted.")
			quit()

		for key in cost.dimensions:
			cost.dimensions[key] = abs(self.dimensions[key] - profileToTest.dimensions[key])

		total = 0
		for key in cost.dimensions:
			cost.dimensions[key] = pow(cost.dimensions[key], 2)
			total += cost.dimensions[key]

		return total


	def distanceBetween(self, profileToTest):
		numDims = len(profileToTest.dimensions)
		return self.sqrDistanceBetween(profileToTest)**(1/float(numDims)) 