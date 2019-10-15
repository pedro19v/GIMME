import numpy
from PlayerStructs import *

class Player(object):
	
	def __init__(self, id, name, currState, pastModelIncreasesGrid, currModelIncreases, personality):
		
		self.currState = currState

		self.id = id
		self.name = name
		self.pastModelIncreasesGrid = pastModelIncreasesGrid

		self.personality = personality; 
		
		# for displaying in charts
		self.currModelIncreases = currModelIncreases; 