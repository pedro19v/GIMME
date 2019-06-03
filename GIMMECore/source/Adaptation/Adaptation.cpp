#include "../../headers/Adaptation/Adaptation.h"

Adaptation::Adaptation()
{
}

Adaptation::Adaptation(
	std::string name,
	std::vector<Player*>* players,
	int numberOfConfigChoices,
	int minNumberOfPlayersPerGroup, int maxNumberOfPlayersPerGroup,
	RegressionAlg* regAlg,
	ConfigsGenAlg* configsGenAlg,
	FitnessAlg* fitAlg,
	RandomGen* randomGen,
	int numTasksPerGroup,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks) {

	this->name = name;
	this->players = players;

	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup;
	this->minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup;

	this->numTasksPerGroup = numTasksPerGroup;
	this->regAlg = regAlg;
	this->fitAlg = fitAlg;
	this->configsGenAlg = configsGenAlg;
	this->configsGenAlg->init(players);

	this->randomGen = randomGen;

	this->possibleCollaborativeTasks = possibleCollaborativeTasks;
	this->possibleCompetitiveTasks = possibleCompetitiveTasks;
	this->possibleIndividualTasks = possibleIndividualTasks;
}

Adaptation::Adaptation(std::string name, std::vector<Player*>* players, int numberOfConfigChoices, int minNumberOfPlayersPerGroup, int maxNumberOfPlayersPerGroup, RegressionAlg * regAlg, ConfigsGenAlg * configsGenAlg, FitnessAlg * fitAlg, RandomGen * randomGen, int numTasksPerGroup)
{
	this->name = name;
	this->players = players;

	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfPlayersPerGroup = maxNumberOfPlayersPerGroup;
	this->minNumberOfPlayersPerGroup = minNumberOfPlayersPerGroup;

	this->numTasksPerGroup = numTasksPerGroup;
	this->regAlg = regAlg;
	this->fitAlg = fitAlg;
	this->configsGenAlg = configsGenAlg;
	this->configsGenAlg->init(players);

	this->randomGen = randomGen;


	this->possibleCollaborativeTasks = std::vector<AdaptationTask>();
	this->possibleCompetitiveTasks = std::vector<AdaptationTask>();
	this->possibleIndividualTasks = std::vector<AdaptationTask>();
}

Adaptation::~Adaptation()
{
	/*if (this->regAlg != NULL) {
		delete regAlg;
	}
	if (this->fitAlg != NULL) {
		delete fitAlg;
	}
	if (this->configsGenAlg != NULL) {
		delete configsGenAlg;
	}
	if (this->randomGen != NULL) {
		delete randomGen;
	}*/
}

std::string Adaptation::getName()
{
	return this->name;
}




std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> Adaptation::iterate(int currIteration)
{
	std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> groupMechanicPairs = std::vector<std::pair<AdaptationGroup, AdaptationMechanic>>();

	adaptedConfig = organizePlayers(currIteration);
	std::vector<AdaptationGroup> groups = adaptedConfig.groups;
	int groupsSize = (int) groups.size();
	for (int i = 0; i < groupsSize; i++) {
		AdaptationGroup currGroup = groups[i];
		std::vector<Player*> groupPlayers = currGroup.players;
		int groupPlayersSize = (int) groupPlayers.size();

		for (int j = 0; j < groupPlayersSize; j++) {
			Player* currPlayer = groupPlayers[j];
			currPlayer->setCurrProfile(currGroup.interactionsProfile);
		}

		InteractionsProfile currGroupProfile = currGroup.interactionsProfile;
		PlayerState currGroupState = currGroup.avgLearningState;
		groupMechanicPairs.push_back({ currGroup , generateMechanic(currGroupProfile, currGroupState, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks) });
	}
	
	return groupMechanicPairs;
}
std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> Adaptation::iterate()
{
	return iterate(0);
}

AdaptationConfiguration Adaptation::getCurrAdaptedConfig() {
	return this->adaptedConfig;
}


AdaptationConfiguration Adaptation::organizePlayers(int currIteration) {
	return configsGenAlg->organize(players, numberOfConfigChoices, minNumberOfPlayersPerGroup, maxNumberOfPlayersPerGroup, randomGen, regAlg, fitAlg);
}

AdaptationMechanic Adaptation::generateMechanic(InteractionsProfile bestConfigProfile,
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
