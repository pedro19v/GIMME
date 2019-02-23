#include <algorithm>
#include <numeric>
#include "Student.h"
#include "Globals.h"
#include "Utilities.h"

#include "time.h"

#include <iostream>

struct AdaptationGroup {
private:
	Student::LearningState avgLearningState;
	Utilities::LearningProfile avgPreferences;
	Utilities::LearningProfile learningProfile;
	std::vector<Student*> students;
public:


	void addStudent(Student* student) {

		students.push_back(student);
		int studentsSize = students.size();


		//recalculate averages
		avgLearningState = Student::LearningState();
		avgPreferences.K_cl = 0;
		avgPreferences.K_cp = 0;
		avgPreferences.K_i = 0;

		for (int i = 0; i < studentsSize; i++) {
			Student* currStudent = students[i];
			Utilities::LearningProfile currStudentPreference = currStudent->getInherentPreference();
			avgLearningState.engagement += currStudent->getEngagement() / studentsSize;
			avgLearningState.ability += currStudent->getAbility() / studentsSize;
			avgPreferences.K_cl += currStudentPreference.K_cl / studentsSize;
			avgPreferences.K_cp += currStudentPreference.K_cp / studentsSize;
			avgPreferences.K_i += currStudentPreference.K_i / studentsSize;
		}
		
	}
	std::vector<Student*> getStudents() {
		return this->students;
	}
	void setLearningProfile(Utilities::LearningProfile learningProfile) {
		this->learningProfile = learningProfile;
	}

	Utilities::LearningProfile getLearningProfile() {
		return this->learningProfile;
	}
	Student::LearningState getAvgLearningState() {
		return this->avgLearningState;
	}
	Utilities::LearningProfile getAvgPreferences() {
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
	struct FitnessSort {
		Adaptation* owner;
		Utilities::LearningProfile testedProfile;

		FitnessSort(Adaptation* owner, Utilities::LearningProfile testedProfile) { 
			this->owner = owner;
			this->testedProfile = testedProfile;
		}

		bool operator () (Student::LearningState& i, Student::LearningState& j) {
			
			double dist1 = testedProfile.distanceBetween(i.currProfile);
			double dist2 = testedProfile.distanceBetween(j.currProfile);

			i.dist = dist1;
			j.dist = dist2;

			return dist1 < dist2;
		}
	};

private:
	int numberOfConfigChoices;
	int maxNumberOfStudentsPerGroup;
	int minNumberOfStudentsPerGroup;

	int numTasksPerGroup;

	int numberOfFitnessNNs;
	int fitnessCondition;

	int numAdaptationCycles;

	AdaptationConfiguration adaptedConfig;

	AdaptationConfiguration organizeStudents(std::vector<Student*> students, int currIteration);
	std::vector<AdaptationTask> generateMechanic(Utilities::LearningProfile bestConfigProfile,
		Student::LearningState avgLearningState,
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);
	AdaptationTask pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, Student::LearningState avgLearningState);

	double fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs, int currIteration);

public:
	Adaptation(int studentSize, int numberOfConfigChoices, int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, int numberOfFitnessNNs, int fitnessCondition, int numAdaptationCycles, int numTasksPerGroup);
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

};