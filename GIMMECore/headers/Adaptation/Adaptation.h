#pragma once

#include <algorithm>
#include <numeric>
#include "../Player/Player.h"
#include "../AuxStructs/RandomGen.h"

#include "../Adaptation/AdaptationStructs.h"

#include "AlgDefStructs/RegressionAlg.h"
#include "AlgDefStructs/ConfigsGenAlg.h"
#include "AlgDefStructs/FitnessAlg.h"

#include <string>
#include "../../../GIMMESim/headers/SimPlayer.h"

class Adaptation {
private:

	//players model refs
	std::vector<Player*>* players; 

	//possible tasks
	std::vector<AdaptationTask> possibleCollaborativeTasks;
	std::vector<AdaptationTask> possibleCompetitiveTasks;
	std::vector<AdaptationTask> possibleIndividualTasks;

	int numberOfConfigChoices;
	int minNumberOfPlayersPerGroup;
	int maxNumberOfPlayersPerGroup;

	int numTasksPerGroup;

	RandomGen* randomGen;

	RegressionAlg* regAlg;
	ConfigsGenAlg* configsGenAlg;
	FitnessAlg* fitAlg;

	AdaptationConfiguration adaptedConfig;
	AdaptationConfiguration organizePlayers(int currIteration);
	AdaptationMechanic generateMechanic(InteractionsProfile bestConfigProfile,
		PlayerState avgLearningState,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	AdaptationTask pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, PlayerState avgLearningState);

public:
	Adaptation();
	Adaptation(
		std::string name,
		std::vector<Player*>* players,
		int numberOfConfigChoices,
		int minNumberOfPlayersPerGroup, int maxNumberOfPlayersPerGroup,
		RegressionAlg* regAlg,
		ConfigsGenAlg* configsGenAlg,
		FitnessAlg* fitAlg,
		RandomGen* randomGen, int numTasksPerGroup,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	Adaptation(
		std::string name,
		std::vector<Player*>* players,
		int numberOfConfigChoices,
		int minNumberOfPlayersPerGroup, int maxNumberOfPlayersPerGroup,
		RegressionAlg* regAlg,
		ConfigsGenAlg* configsGenAlg,
		FitnessAlg* fitAlg,
		RandomGen* randomGen, int numTasksPerGroup);
	~Adaptation();

	std::string getName();

	AdaptationConfiguration iterate();
	AdaptationConfiguration iterate(int currIteration);

	AdaptationConfiguration getCurrAdaptedConfig();

	//adaptation metrics
	std::vector<double> avgAbilities;
	std::vector<double> avgEngagements;
	std::vector<double> avgPrefDiff;
	double avgExecutionTime;

	std::string name;
};