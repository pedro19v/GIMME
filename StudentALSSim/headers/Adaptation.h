#include <algorithm>
#include <numeric>
#include "Student.h"
#include "Globals.h"
#include "Utilities.h"

#include "time.h"

struct AdaptationGroup {
public:
	Utilities::LearningProfile profile;
	std::vector<Student*> students;

	double fitness;
};


struct AdaptationConfiguration {
public:
	std::vector<AdaptationGroup> groups;
	double fitness;
};

struct AdaptationMechanic {
public:
	std::string name;
};

class Adaptation {
private:
	struct FitnessSort {
		Student* currStudent;

		FitnessSort(Student* currStudent) { this->currStudent = currStudent; }
		bool operator () (Student::StudentModel i, Student::StudentModel j) {
			double IprofileValue = i.currProfile.K_cl + i.currProfile.K_cp + i.currProfile.K_i;
			double JprofileValue = j.currProfile.K_cl + j.currProfile.K_cp + j.currProfile.K_i;

			double currProfileValue = currStudent->getCurrProfile().K_cl + currStudent->getCurrProfile().K_cp + currStudent->getCurrProfile().K_i;
			return (std::abs(IprofileValue - currProfileValue) > std::abs(JprofileValue - currProfileValue));
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