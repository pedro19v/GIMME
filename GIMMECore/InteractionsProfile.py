import math

class InteractionsProfile(object):

	def __init__(self, K_cp=0, K_i=0, K_mh=0, K_ea=0):
		self.K_cp = K_cp
		self.K_i = K_i
		self.K_mh = K_mh
		self.K_ea = K_ea

	def reset(self):
		self.K_cp = 0
		self.K_i = 0
		self.K_mh = 0
		self.K_ea = 0

	def normalize(self):
		total = self.K_cp + self.K_i + self.K_mh + self.K_ea
		if(total==0):
			self.K_cp = 0.25
			self.K_i = 0.25
			self.K_mh = 0.25
			self.K_ea = 0.25
		else:
			self.K_cp = self.K_cp / total
			self.K_i = self.K_i / total
			self.K_mh = self.K_mh / total
			self.K_ea = self.K_ea / total

	def normalizedDistanceBetween(self, profileToTest):
		thisProfile = self
		cost = InteractionsProfile()

		# normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cp = abs(thisProfile.K_cp - profileToTest.K_cp)
		cost.K_i = abs(thisProfile.K_i - profileToTest.K_i)
		cost.K_mh = abs(thisProfile.K_mh - profileToTest.K_mh)
		cost.K_ea = abs(thisProfile.K_pa - profileToTest.K_pa)

		cost.normalize()

		cost.K_cp = pow(cost.K_cp, 2)
		cost.K_i = pow(cost.K_i, 2)
		cost.K_mh = pow(cost.K_mh, 2)
		cost.K_ea = pow(cost.K_pa, 2)

		return math.sqrt(cost.K_cp + cost.K_i + cost.K_mh + cost.K_pa)
	

	def sqrDistanceBetween(self, profileToTest):
		thisProfile = self
		cost = InteractionsProfile()

		# normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cp = thisProfile.K_cp - profileToTest.K_cp
		cost.K_i = thisProfile.K_i - profileToTest.K_i
		cost.K_mh = thisProfile.K_mh - profileToTest.K_mh
		cost.K_ea = thisProfile.K_ea - profileToTest.K_ea

		cost.K_cp = pow(cost.K_cp, 2)
		cost.K_i = pow(cost.K_i, 2)
		cost.K_mh = pow(cost.K_mh, 2)
		cost.K_ea = pow(cost.K_ea, 2)

		return cost.K_cp + cost.K_i + cost.K_mh + cost.K_ea


	def distanceBetween(self, profileToTest):
		return math.sqrt(self.sqrDistanceBetween(profileToTest))