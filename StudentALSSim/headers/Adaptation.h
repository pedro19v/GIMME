#include <algorithm>
#include <numeric>
#include "Student.h"
#include "Globals.h"
#include "Utilities.h"

#include "time.h"

#include <iostream>

struct AdaptationGroup {
public:

	Utilities::LearningProfile profile;
	std::vector<Student*> students;

	double avgEngagement;
	double avgAbility;
	Utilities::LearningProfile avgPreferences;
	
	void addStudent(Student* student) {
		students.push_back(student);
		int studentsSize = students.size();


		//recalculate averages
		avgEngagement = 0;
		avgAbility = 0;
		avgPreferences.K_cl = 0;
		avgPreferences.K_cp = 0;
		avgPreferences.K_i = 0;

		for (int i = 0; i < studentsSize; i++) {
			Student* currStudent = students[i];
			Utilities::LearningProfile currStudentPreference = currStudent->getInherentPreference();
			avgEngagement += currStudent->getEngagement() / studentsSize;
			avgAbility += currStudent->getAbility() / studentsSize;
			avgPreferences.K_cl += currStudentPreference.K_cl / studentsSize;
			avgPreferences.K_cp += currStudentPreference.K_cp / studentsSize;
			avgPreferences.K_i += currStudentPreference.K_i / studentsSize;
		}
		
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
public:
	AdaptationTaskType type;
	std::string description;
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

		bool operator () (Student::StudentModel& i, Student::StudentModel& j) {
			
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

	AdaptationConfiguration adaptedConfig;

	AdaptationConfiguration organizeStudents(std::vector<Student*> students, int currIteration);
	std::vector<AdaptationTask> generateMechanic(Utilities::LearningProfile bestConfigProfile, 
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks);

	double fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs, int currIteration);
public:
	Adaptation(int studentSize, int numberOfConfigChoices, int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, int numberOfFitnessNNs, int fitnessCondition, int numAdaptationCycles, int numTasksPerGroup);
	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> iterate(std::vector<Student*> students, 
		std::vector<AdaptationTask> possibleCollaborativeTasks,
		std::vector<AdaptationTask> possibleCompetitiveTasks,
		std::vector<AdaptationTask> possibleIndividualTasks, 
		int currIteration);
	
	AdaptationConfiguration getCurrAdaptedConfig();



	std::vector<double> avgAbilities;
	std::vector<double> avgEngagements;
	std::vector<double> avgPrefDiff;
	double avgExecutionTime;

	std::vector<int> groupSizeFreqs;
	std::vector<int> configSizeFreqs;

};