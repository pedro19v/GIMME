import random
import time
import numpy

class RandomGen(object):

# public:
	def __init__(self):
		self.defaultRandomSeed = time.time();
		random.seed(self.defaultRandomSeed)

	def resetRandoms(seed = None):
		random.seed(self.defaultRandomSeed)

	def randBetween(seed = None, min, max):
		if(seed):
			random.seed(self.defaultRandomSeed)
		return random.randrange(min, max)

	def randIntBetween(seed = None, min, max):
		if(seed):
			random.seed(self.defaultRandomSeed)
		return random.randint(min, max)

	def randShuffle(array):
		return random.shuffle(array)

	def normalRandom(seed=None, mu, var):
		if(seed):
			random.seed(self.defaultRandomSeed)
		return random.gauss(mu,var)
};