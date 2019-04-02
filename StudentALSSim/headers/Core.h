#pragma once
#include "Utilities.h"
#include "Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

class Core {
private:
	int numRuns = 30;
	int numTrainingCycles = 30;
	const int numStudentModelCells = 1;

	int numAdaptationConfigurationChoices = 100;
	int timeWindow = 30;
	int maxNumStudentsPerGroup = 5;
	int minNumStudentsPerGroup = 2;

	int numTasksPerGroup = 3;

	int numStudentsInClass;
	int numStudentModelCells;
	int maxAmountOfStoredProfilesPerCell;
	std::vector<Student*>  students;

	std::vector<AdaptationTask> possibleCollaborativeTasks;
	std::vector<AdaptationTask> possibleCompetitiveTasks;
	std::vector<AdaptationTask> possibleIndividualTasks;

	Utilities* utilities;

	std::ofstream statisticsFile;
	std::ofstream resultsFile;

	Core(int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell, int numIterations,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	~Core();
	void reset();

	void simulateStudentsReaction(int currIteration);

	void simulateTrainingPhase();
	void storeSimData(std::string configId, Adaptation* adapt);
	void executeSimulation(int numRuns, Adaptation* adapt);

	void executeAdaptationStep(int currStepIndex, int currRun, Adaptation* adapt);
	void simulateAdaptationModule(int currRun, Adaptation* adapt, int initialStep);
public:

};