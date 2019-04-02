#pragma once

#include <algorithm>
#include <numeric>
#include "Student.h"
#include "GlobalStructs.h"
#include "Utilities.h"

#include "time.h"

#include <iostream>


class Adaptation {

public:

	Adaptation(int studentSize, int numberOfConfigChoices, int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, int numberOfFitnessNNs, int fitnessCondition, int numAdaptationCycles, int numTasksPerGroup, Utilities* utilities);
	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> iterate(std::vector<Student*> students,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks,
		int currIteration);

	AdaptationConfiguration getCurrAdaptedConfig();
	int getNumAdaptationCycles();



	std::vector<double> avgAbilities;
	std::vector<double> avgEngagements;
	std::vector<double> avgPrefDiff;
	double avgExecutionTime;

	std::vector<int> groupSizeFreqs;
	std::vector<int> configSizeFreqs;

private:
	struct FitnessSort {
		Adaptation* owner;
		InteractionsProfile testedProfile;

		FitnessSort(Adaptation* owner, InteractionsProfile testedProfile) {
			this->owner = owner;
			this->testedProfile = testedProfile;
		}

		bool operator () (LearningState& i, LearningState& j) {
			
			double dist1 = testedProfile.distanceBetween(i.currProfile);
			double dist2 = testedProfile.distanceBetween(j.currProfile);

			i.dist = dist1;
			j.dist = dist2;

			return dist1 < dist2;
		}
	};

	int numberOfConfigChoices;
	int maxNumberOfStudentsPerGroup;
	int minNumberOfStudentsPerGroup;

	int numTasksPerGroup;
	int numberOfFitnessNNs;
	int fitnessCondition;
	int numAdaptationCycles;

	Utilities* utilities;

	AdaptationConfiguration adaptedConfig;
	AdaptationConfiguration organizeStudents(std::vector<Student*> students, int currIteration);
	std::vector<AdaptationTask> generateMechanic(InteractionsProfile bestConfigProfile,
		LearningState avgLearningState,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	AdaptationTask pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, LearningState avgLearningState);

	double fitness(Student* student, InteractionsProfile profile, int numberOfFitnessNNs, int currIteration);



};