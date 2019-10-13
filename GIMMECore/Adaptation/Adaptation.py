import math

class Adaptation(object):
	def init(self, name="", \
		numberOfConfigChoices=100, \
		minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5, \
		regAlg = RegressionAlg(), \
		configsGenAlg = ConfigsGenAlg(), \
		fitAlg = FitnessAlg(), \
		randomGen = RandomGen(), \
		modelsConnector = ModelsConnector(),
		difficultyWeight = 0.5, 
		profileWeight=0.5):
		
		self.name = name;
		self.players = players;

		self.numberOfConfigChoices = numberOfConfigChoices;
		self.maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup;
		self.minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup;

		self.numTasksPerGroup = numTasksPerGroup;
		self.regAlg = regAlg;
		self.fitAlg = fitAlg;
		self.configsGenAlg = configsGenAlg;
		self.configsGenAlg.init(players);

		self.randomGen = randomGen;

		self.difficultyWeight = difficultyWeight
		self.profileWeight = profileWeight

	def getName(self):
		return self.name;


	def iterate(tasks, playerIDs):
		adaptedConfig = organizePlayers(playerIDs);
		groups = adaptedConfig.groups;
		groupsSize = len(groups);
		for i in range(groupsSize):
			currGroup = groups[i];
			groupPlayers = modelsConnector.getPlayersById(currGroup.players);
			int groupPlayersSize = (int) groupPlayers.size();

			for j in range(groupPlayersSize):
				currPlayer = modelsConnector.getPlayersById([j]);
				currPlayer.setCurrProfile(currGroup.interactionsProfile);

			currGroupProfile = currGroup.interactionsProfile;
			currGroupState = currGroup.avgPlayerState;
			currGroup.tailoredTask = generateMechanic(tasks, currGroupProfile, currGroupState, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks);
		return adaptedConfig;


	def organizePlayers(playerIDs):
		return self.configsGenAlg.organize(playerIDs, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, randomGen, regAlg, fitAlg);

	def selectTask(possibleTasks,
		bestConfigProfile,
		avgLearningState):
		lowestCost = math.inf
		for i in range(len(possibleTasks)):
			currTask = possibleTasks[i]
			cost += abs(bestConfigProfile.distanceBetween(currTask.interactionsProfile) *currTask.difficultyWeight)
			cost += abs(avgLearningState.ability - currTask.minRequiredAbility * currTask.profileWeight)

			if cost < lowestCost:
				lowestCost = cost
