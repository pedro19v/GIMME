#pragma once

#include <algorithm>
#include <numeric>
#include "Student.h"
#include "Utilities.h"

#include <iostream>


struct AdaptationGroup {
private:
	PlayerState avgLearningState;
	InteractionsProfile avgPreferences;
	InteractionsProfile interactionsProfile;
	std::vector<Student*> students;
public:

	void addStudent(Student* student) {
		students.push_back(student);
		int studentsSize = (int) students.size();

		//recalculate averages
		avgLearningState = PlayerState();
		avgPreferences.K_cl = 0;
		avgPreferences.K_cp = 0;
		avgPreferences.K_i = 0;

		for (int i = 0; i < studentsSize; i++) {
			Student* currStudent = students[i];
			//InteractionsProfile currStudentPreference = currStudent->getInherentPreference();
			avgLearningState.characteristics.engagement += currStudent->getCurrState().characteristics.engagement / studentsSize;
			avgLearningState.characteristics.ability += currStudent->getCurrState().characteristics.ability / studentsSize;
			/*avgPreferences.K_cl += currStudentPreference.K_cl / studentsSize;
			avgPreferences.K_cp += currStudentPreference.K_cp / studentsSize;
			avgPreferences.K_i += currStudentPreference.K_i / studentsSize;*/
		}

	}
	std::vector<Student*> getStudents() {
		return this->students;
	}
	void setInteractionsProfile(InteractionsProfile learningProfile) {
		this->interactionsProfile = learningProfile;
	}

	InteractionsProfile getInteractionsProfile() {
		return this->interactionsProfile;
	}
	PlayerState getAvgLearningState() {
		return this->avgLearningState;
	}
	InteractionsProfile getAvgPreferences() {
		return this->avgPreferences;
	}
};
struct AdaptationConfiguration {
public:
	std::vector<AdaptationGroup> groups;
};
enum AdaptationTaskType {
	COLLABORATION = 0,
	COMPETITION = 1,
	SELF_INTERACTION = 2
};
struct AdaptationTask {
private:
	/*struct WayToSortTaskInstances {
		bool operator()(const AdaptationTask& i, const AdaptationTask& j) { return i.minRequiredAbility < j.minRequiredAbility; }
	};*/
public:
	AdaptationTaskType type;
	std::string description;
	float minRequiredAbility;
	std::vector<AdaptationTask> taskInstances; //maintained in order

	AdaptationTask(AdaptationTaskType type, std::string description, float minRequiredAbility, std::vector<AdaptationTask> taskInstances) {
		this->type = type;
		this->description = description;
		this->minRequiredAbility = minRequiredAbility;

		//std::sort(taskInstances.begin(), taskInstances.end(), WayToSortTaskInstances());
		this->taskInstances = taskInstances;
	}
	AdaptationTask(AdaptationTaskType type, std::string description, std::vector<AdaptationTask> taskInstances) : AdaptationTask(type, description, 0, taskInstances) {}
	AdaptationTask(AdaptationTaskType type, std::string description, float minRequiredAbility) : AdaptationTask(type, description, minRequiredAbility, std::vector<AdaptationTask>()) {}
};


class Adaptation {

private:

	//students model refs
	std::vector<Student*> students; 

	//possible tasks
	std::vector<AdaptationTask> possibleCollaborativeTasks;
	std::vector<AdaptationTask> possibleCompetitiveTasks;
	std::vector<AdaptationTask> possibleIndividualTasks;

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
		PlayerState avgLearningState,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	AdaptationTask pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, PlayerState avgLearningState);

	double fitness(Student* student, InteractionsProfile profile, int numberOfFitnessNNs, int currIteration);


	struct FitnessSort {
		Adaptation* owner;
		InteractionsProfile testedProfile;

		FitnessSort(Adaptation* owner, InteractionsProfile testedProfile) {
			this->owner = owner;
			this->testedProfile = testedProfile;
		}

		bool operator () (PlayerState& i, PlayerState& j) {
			
			double dist1 = testedProfile.distanceBetween(i.profile);
			double dist2 = testedProfile.distanceBetween(j.profile);

			i.dist = dist1;
			j.dist = dist2;

			return dist1 < dist2;
		}
	};


public:

	Adaptation(
		std::vector<Student*> students, 
		int numberOfConfigChoices,
		int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup,
		int numberOfFitnessNNs, int fitnessCondition,
		int numAdaptationCycles, 
		Utilities* utilities, int numTasksPerGroup,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks
	);
	

	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> iterate();
	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> iterate(int currIteration);

	AdaptationConfiguration getCurrAdaptedConfig();
	int getNumAdaptationCycles();


	//adaptation metrics
	std::vector<double> avgAbilities;
	std::vector<double> avgEngagements;
	std::vector<double> avgPrefDiff;
	double avgExecutionTime;

	std::vector<int> groupSizeFreqs;
	std::vector<int> configSizeFreqs;
};