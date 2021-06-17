import random
import json
import os
import sys
import textwrap

from datetime import datetime, timedelta

sys.path.insert(1,'/home/samgomes/Documents/doutoramento/reps/GIMME/GIMME')
sys.path.insert(1,'/GIMME')
sys.path.insert(1,'../')
from GIMMECore import *
from ModelMocks import *


print("------------------------------------------")
print("-----                                -----")
print("-----     SIMPLE GIMME API TEST      -----")
print("-----                                -----")
print("------------------------------------------")

numPlayers = 20#int(input("How many players would you like? "))
numTasks = 5#int(input("How many tasks would you like? "))
adaptationGIMME = Adaptation() 

players = [0 for x in range(numPlayers)]
tasks = [0 for x in range(numTasks)]


preferredNumberOfPlayersPerGroup = 4#int(input("How many players per group would you prefer? "))

playerBridge = CustomPlayerModelBridge(players)
taskBridge = CustomTaskModelBridge(tasks)

profileTemplate = InteractionsProfile({"dim_0": 0, "dim_1": 0})


print("Setting up the players...")

for x in range(numPlayers):
	playerBridge.registerNewPlayer(
		playerId = int(x), 
		name = "name", 
		currState = PlayerState(profile = profileTemplate.generateCopy().reset()), 
		pastModelIncreasesGrid = PlayerStateGrid(
			interactionsProfileTemplate = profileTemplate.generateCopy().reset(), 
			gridTrimAlg = QualitySortGridTrimAlg(
				maxNumModelElements = 30, 
				qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
				), 
			numCells = 1
			), 
		currModelIncreases = PlayerCharacteristics(), 
		personalityEst = profileTemplate.generateCopy().reset(), 
		realPersonality = profileTemplate.generateCopy().reset())
	playerBridge.resetState(x)
	playerBridge.getPlayerStateGrid(x).gridTrimAlg.considerStateResidue(True)

	# init players including predicted personality
	playerBridge.resetPlayer(x)

	playerBridge.setPlayerPersonalityEst(x, profileTemplate.generateCopy().init())
	# realPersonality = realPersonalities[x]
	# playerBridge.setPlayerRealPersonality(x, realPersonality)

	playerBridge.setPlayerRealPersonality(x, profileTemplate.randomized())
	playerBridge.setBaseLearningRate(x, 0.5)

	playerBridge.getPlayerStateGrid(x).gridTrimAlg.considerStateResidue(False)

print("Players created.")

print("\nSetting up the tasks...")

for x in range(numTasks):
	diffW = random.uniform(0, 1)
	profW = 1 - diffW
	taskBridge.registerNewTask(
		taskId = int(x), 
		description = "description", 
		minRequiredAbility = random.uniform(0, 1), 
		profile = profileTemplate.randomized(), 
		minDuration = str(timedelta(minutes=1)), 
		difficultyWeight = diffW, 
		profileWeight = profW)

print("Tasks created:")
print(json.dumps(taskBridge.tasks, default=lambda o: o.__dict__, sort_keys=True, indent=2))

print("\nSetting up a random group. org. algorithm...")





def simulateReaction(isBootstrap, playerBridge, playerId):
	currState = playerBridge.getPlayerCurrState(playerId)
	newState = calcReaction(
		isBootstrap = isBootstrap, 
		playerBridge = playerBridge, 
		state = currState, 
		playerId = playerId)

	increases = PlayerState(stateType = newState.stateType)
	increases.profile = currState.profile
	increases.characteristics = PlayerCharacteristics(ability=(newState.characteristics.ability - currState.characteristics.ability), engagement=newState.characteristics.engagement)
	playerBridge.setAndSavePlayerStateToGrid(playerId, increases, newState)	
	return increases

def calcReaction(isBootstrap, playerBridge, state, playerId):
	personality = playerBridge.getPlayerRealPersonality(playerId)
	numDims = len(personality.dimensions)
	newStateType = 0 if isBootstrap else 1
	newState = PlayerState(
		stateType = newStateType, 
		characteristics = PlayerCharacteristics(
			ability=state.characteristics.ability, 
			engagement=state.characteristics.engagement
			), 
		profile=state.profile)
	newState.characteristics.engagement = 1 - (personality.distanceBetween(state.profile) / math.sqrt(numDims))  #between 0 and 1
	if newState.characteristics.engagement>1:
		breakpoint()
	abilityIncreaseSim = (newState.characteristics.engagement*playerBridge.getBaseLearningRate(playerId))
	newState.characteristics.ability = newState.characteristics.ability + abilityIncreaseSim
	return newState






numberOfConfigChoices = 100
numTestedPlayerProfilesInEst = 500
regAlg = KNNRegression(playerBridge, 5)
simpleConfigsAlg = StochasticHillclimberConfigsGen(
	playerModelBridge = playerBridge, 
	interactionsProfileTemplate = profileTemplate.generateCopy(), 
	regAlg = regAlg, 
	persEstAlg = ExplorationPersonalityEstAlg(
		playerModelBridge = playerBridge, 
		interactionsProfileTemplate = profileTemplate.generateCopy(), 
		regAlg = regAlg,
		numTestedPlayerProfiles = numTestedPlayerProfilesInEst, 
		qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)), 
	numberOfConfigChoices = numberOfConfigChoices, 
	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup, 
	qualityWeights = PlayerCharacteristics(ability=0.5, engagement=0.5)
)
adaptationGIMME.init(
	playerModelBridge = playerBridge, 
	taskModelBridge = taskBridge,
	configsGenAlg = simpleConfigsAlg, 
	name="Test Adaptation"
)



# randomConfigsAlg = RandomConfigsGen(
# 	playerModelBridge = playerBridge, 
# 	interactionsProfileTemplate = profileTemplate.generateCopy(), 
# 	preferredNumberOfPlayersPerGroup = preferredNumberOfPlayersPerGroup
# )
# adaptationGIMME.init(
# 	playerModelBridge = playerBridge, 
# 	taskModelBridge = taskBridge,
# 	configsGenAlg = randomConfigsAlg, 
# 	name="Test Adaptation"
# )


ready = True
while(True):
	readyText = ""
	readyText = str(input("Ready to compute iteration (y/n)? "))
	while(readyText!="y" and readyText!="n"):
		readyText = str(input("Please answer y/n: "))
	ready = (readyText=="y")
	if(not ready):
		print("~~~~~~(The End)~~~~~~")
		break


	print("----------------------")
	print("Iteration Summary:\n\n\n")
	print(json.dumps(adaptationGIMME.iterate(), default=lambda o: o.__dict__, sort_keys=True))

	print("----------------------\n\n\n")
	print("Player States:\n\n\n")
	for x in range(numPlayers):
		increases = simulateReaction(False, playerBridge, x)
		print(json.dumps(playerBridge.getPlayerCurrState(x), default=lambda o: o.__dict__, sort_keys=True))


	print("~~~~~~~~~~~~~~~~~~~~~\n\n\n")
