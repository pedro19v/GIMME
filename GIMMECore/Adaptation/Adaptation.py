#include "..//..//headers//Adaptation//Adaptation.h"

class Adaptation(object):
	def init(self, name="", databaseAdapter, \
		numberOfConfigChoices=100, \
		minNumberOfPlayersPerGroup = 2, maxNumberOfPlayersPerGroup = 5, \
		regAlg = RegressionAlg(), \
		configsGenAlg = ConfigsGenAlg(), \
		fitAlg = FitnessAlg(), \
		randomGen = RandomGen(), \
		modelsConnector = ModelsConnector()):
		
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


	def getName(self):
		return self.name;


	def iterate(tasks):
		adaptedConfig = organizePlayers();
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
			currGroup.tailoredTask = generateMechanic(currGroupProfile, currGroupState, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks);

		return adaptedConfig;


	def organizePlayers(int currIteration):
		return self.configsGenAlg.organize(playerIDs, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, randomGen, regAlg, fitAlg);


	def selectMechanic(InteractionsProfile bestConfigProfile,
	PlayerState avgLearningState,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks) {

	
	int collaborativeTaskSize = (int) ceil(bestConfigProfile.K_cl*numTasksPerGroup);
	int competitiveTaskSize = (int) ceil(bestConfigProfile.K_cp*numTasksPerGroup);
	int individualTaskSize = (int) ceil(bestConfigProfile.K_i*numTasksPerGroup);

	std::vector<AdaptationTask> mechanicTasks = std::vector<AdaptationTask>();
	
	for (int i = 0; i < collaborativeTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(possibleCollaborativeTasks, avgLearningState));
	}
	for (int i = 0; i < competitiveTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(possibleCompetitiveTasks, avgLearningState));
	}
	for (int i = 0; i < individualTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(possibleIndividualTasks, avgLearningState));
	}
	randomGen->randShuffle(mechanicTasks);

	AdaptationMechanic mechanic = { bestConfigProfile, mechanicTasks };
	return mechanic;
}

AdaptationTask Adaptation::pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, PlayerState avgLearningState)
{
	if (possibleTasks.empty()) {
		return AdaptationTask{ AdaptationTaskType::NONE, "default", 0.0f };
	}
	int randIndex = randomGen->randIntBetween(0, (int) possibleTasks.size() - 1);
	AdaptationTask randomTask = possibleTasks[randIndex];
	std::vector<AdaptationTask> randomTaskInstances = randomTask.taskInstances;
	int randomTaskInstancesSize = (int) randomTaskInstances.size();
	
	//pick the right difficulty
	AdaptationTask adaptedInstance = randomTaskInstances[0];
	for (int j = 1; j < randomTaskInstancesSize; j++) {
		AdaptationTask currInstance = randomTaskInstances[j];
		float minRequiredAbility = currInstance.minRequiredAbility;
		if (minRequiredAbility < avgLearningState.characteristics.ability && minRequiredAbility > adaptedInstance.minRequiredAbility) {
			adaptedInstance = currInstance;
		}
	}
	return adaptedInstance;
}
 
