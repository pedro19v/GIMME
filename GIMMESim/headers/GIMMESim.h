#pragma once

#include <cmath>
#include <fstream>
#include <ios>
#include "../../GIMMECore/headers/GIMMECore.h"
#include "../headers/SimPlayer.h"

class GIMMESim {
private:
	int numRuns;
	int numIterationsPerRun;
	int numTrainingCycles;

	int numConfigurationChoices;
	int numFitnessNNs;
	int timeWindow;
	int maxNumStudentsPerGroup;
	int minNumStudentsPerGroup;

	int numTasksPerGroup;

	int numStudentsInClass;
	int numStudentModelCells;
	int maxAmountOfStoredProfilesPerCell;
	std::vector<Player*>  students;

	std::vector<AdaptationTask> possibleCollaborativeTasks;
	std::vector<AdaptationTask> possibleCompetitiveTasks;
	std::vector<AdaptationTask> possibleIndividualTasks;

	Adaptation* adapt;
	RandomGen* randomGen;

	std::fstream* statisticsFile;
	std::fstream* resultsFile;

	ConfigsGenAlg* configsGenAlg;
	FitnessAlg* fitnessAlg;
	RandomFitness* randomFitness;
	RegressionAlg* regAlg;

	void reset();

	void simulateStudentsReaction(int currIteration);

	void simulateTrainingPhase(int currRun);
	void storeSimData(std::string configId, Adaptation* adapt);

	void executeAdaptationStep(int currStepIndex, int currRun);
	void simulateAdaptationModule(int currRun, Adaptation* adapt, int initialStep, int numIterations);
public:
	GIMMESim(
		int numRuns, int numIterationsPerRun, int numTrainingCycles,
		int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell,
		int numConfigurtionChoices, int numFitnessNNs, int timeWindow,
		int minNumStudentsPerGroup, int maxNumStudentsPerGroup,
		int numTasksPerGroup,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	void simulate();
	~GIMMESim();
};