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
	int maxNumberOfPlayersPerGroup;
	int minNumberOfPlayersPerGroup;

	int numTasksPerGroup;
	int fitnessCondition;
	int numAdaptationCycles;

	RandomGen* randomGen;

	RegressionAlg regAlg;
	ConfigsGenAlg configsGenAlg;
	FitnessAlg fitAlg;

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
		RegressionAlg regAlg,
		ConfigsGenAlg configsGenAlg,
		FitnessAlg fitAlg,
		int numAdaptationCycles,
		RandomGen* utilities, int numTasksPerGroup,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks
	);

	Adaptation(
		std::string name,
		std::vector<Player*>* players,
		int numberOfConfigChoices,
		int minNumberOfPlayersPerGroup, int maxNumberOfPlayersPerGroup,
		RegressionAlg regAlg,
		ConfigsGenAlg configsGenAlg,
		FitnessAlg fitAlg,
		RandomGen* utilities, int numTasksPerGroup,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	
	std::string getName();

	std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> iterate();
	std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> iterate(int currIteration);

	AdaptationConfiguration getCurrAdaptedConfig();
	int getNumAdaptationCycles();


	//adaptation metrics
	std::vector<double> avgAbilities;
	std::vector<double> avgEngagements;
	std::vector<double> avgPrefDiff;
	double avgExecutionTime;


	std::string name;
};