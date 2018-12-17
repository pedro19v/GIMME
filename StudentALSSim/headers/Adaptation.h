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
};


struct AdaptationConfiguration {
public:
	std::vector<AdaptationGroup> groups;
};

struct AdaptationMechanic {
public:
	std::string name;
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
			
			double gain1 = owner->calcGain(testedProfile, i.currProfile);
			double gain2 = owner->calcGain(testedProfile, j.currProfile);

			i.gain = gain1;
			j.gain = gain2;

			return gain1 < gain2;
		}
	};

private:
	int numberOfConfigChoices;
	int maxNumberOfStudentsPerGroup;

	int numberOfFitnessNNs;
	bool isRandomFitness;

	AdaptationConfiguration divideStudents(std::vector<Student*> students);
	AdaptationMechanic generateMechanic(Utilities::LearningProfile bestConfigProfile);

	double fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs);
public:
	Adaptation(int numberOfConfigChoices, int maxNumberOfStudentsPerGroup, int numberOfFitnessNNs, bool isRandomFitness);
	std::vector<AdaptationMechanic> iterate(std::vector<Student*> students);

	double calcGain(Utilities::LearningProfile profile1, Utilities::LearningProfile profile2);
};