import math

class InteractionsProfile(object):
# public:
	def __init__(self, K_cl=0, K_cp=0, K_i=0):
		self.K_cl = K_cl
		self.K_cp = K_cp
		self.K_i = K_i

	def reset(self):
		self.K_cl = 0
		self.K_cp = 0
		self.K_i = 0

	def normalizedDistanceBetween(self, profileToTest):
		profile1 = self
		cost = InteractionsProfile()
		# normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = abs(profile1.K_cl - profileToTest.K_cl)
		cost.K_cp = abs(profile1.K_cp - profileToTest.K_cp)
		cost.K_i = abs(profile1.K_i - profileToTest.K_i)

		totalDiff = cost.K_cl + cost.K_cp + cost.K_i

		cost.K_cl /= totalDiff
		cost.K_cp /= totalDiff
		cost.K_i /= totalDiff

		cost.K_cl = pow(cost.K_cl, 2)
		cost.K_cp = pow(cost.K_cl, 2)
		cost.K_i = pow(cost.K_cl, 2)

		return math.sqrt(cost.K_cl + cost.K_cp + cost.K_i)
	

	def distanceBetween(self, profileToTest):
		profile1 = self
		cost = InteractionsProfile()

		# normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = abs(profile1.K_cl - profileToTest.K_cl)
		cost.K_cp = abs(profile1.K_cp - profileToTest.K_cp)
		cost.K_i = abs(profile1.K_i - profileToTest.K_i)

		cost.K_cl = pow(cost.K_cl, 2)
		cost.K_cp = pow(cost.K_cl, 2)
		cost.K_i = pow(cost.K_cl, 2)

		return math.sqrt(cost.K_cl + cost.K_cp + cost.K_i)