import random
import time
import numpy

class RandomGen(object):

# public:
	def __init__(self):
		self.defaultRandomSeed = time.time();
		random.seed(self.defaultRandomSeed)

	def resetRandoms(self, seed = None):
		random.seed(self.defaultRandomSeed)

	def randBetween(self, min, max, seed = None):
		if(seed):
			random.seed(self.defaultRandomSeed)
		return random.randrange(min, max)

	def randIntBetween(self, min, max, seed = None):
		if(seed):
			random.seed(self.defaultRandomSeed)
		return random.randint(min, max)

	def randShuffle(self, array):
		return random.shuffle(array)

	def normalRandom(self, mu, var, seed=None):
		if(seed):
			random.seed(self.defaultRandomSeed)
		return random.gauss(mu,var)