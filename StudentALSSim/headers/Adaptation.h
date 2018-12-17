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

	int numberOfFitnessNNs;
	bool isRandomFitness;

	AdaptationConfiguration divideStudents(std::vector<Student*> students);
	AdaptationMechanic generateMechanic(Utilities::LearningProfile bestConfigProfile);

	double fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs);
public:
	Adaptation(int numberOfConfigChoices, int maxNumberOfStudentsPerGroup, int numberOfFitnessNNs, bool isRandomFitness);
	std::vector<AdaptationMechanic> iterate(std::vector<Student*> students);

};