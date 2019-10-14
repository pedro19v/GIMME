from Adaptation import Adaptation
from AlgDefStructs.RegressionAlg import *
from AlgDefStructs.ConfigsGenAlg import *
from AlgDefStructs.FitnessAlg import *
from Player.PlayerModelBridge import PlayerModelBridge
from Player.PlayerStructs import PlayerCharacteristics
from AuxStructs.InteractionsProfile import InteractionsProfile


class CustomModelBridge(PlayerModelBridge):

	def saveplayerIncreases(self, playerId, stateIncreases):
		return 0

	def resetPlayer(self, playerId):
		return 0


	def getAllPlayerIds(self):
		return [0, 1, 2]
	

	def getPlayerName(self, playerId):
		return "name"

	def getPlayerCurrProfile(self,  playerId):
		return InteractionsProfile(0.2,0.3,0.5)

	def getPlayerPastModelIncreases(self, playerId):
		return [PlayerState(characteristics = PlayerCharacteristics(0.2,0.3)),PlayerState(characteristics = PlayerCharacteristics(0.5,0.3)),PlayerState(characteristics = PlayerCharacteristics(0.2,0.8))]

	def getPlayerCurrState(self, playerId):
		return PlayerState(characteristics=PlayerCharacteristics(0.3,0.8))
	
	def getPlayerPersonality(self, playerId):
		return InteractionsProfile(0.1,0.2,0.5)


	def setPlayerCharacteristics(self, playerId, characteristics):
		pass

	def setPlayerCurrProfile(self, playerId, profile):
		pass

adaptation = Adaptation()
adaptation.init(KNNRegression(5), RandomConfigsGen(), WeightedFitness(PlayerCharacteristics(ability=0.5, engagement=0.5)), CustomModelBridge(), name="", numberOfConfigChoices=50, maxNumberOfPlayersPerGroup = 10, difficultyWeight = 0.5, profileWeight=0.5)
adaptation.iterate()