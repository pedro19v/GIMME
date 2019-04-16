#pragma once

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>
#include "../../GIMMECore/headers/GIMMECore.h"
#include "../headers/SimStudent.h"

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
	std::vector<Student*>  students;

	std::vector<AdaptationTask> possibleCollaborativeTasks;
	std::vector<AdaptationTask> possibleCompetitiveTasks;
	std::vector<AdaptationTask> possibleIndividualTasks;

	Adaptation* adapt;
	Utilities* utilities;

	std::ofstream* statisticsFile;
	std::ofstream* resultsFile;

	void reset();

	void simulateStudentsReaction(int currIteration);

	void simulateTrainingPhase();
	void storeSimData(std::string configId, Adaptation* adapt);

	void executeAdaptationStep(int currStepIndex, int currRun);
	void simulateAdaptationModule(int currRun, Adaptation* adapt, int initialStep);
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