#include <algorithm>
#include <numeric>
#include "Sim.h"

#include "time.h"

struct AdaptationGroup {
public:
	LearningProfile profile;
	std::vector<Student> students;

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
	int numberOfConfigChoices;
	int maxNumberOfStudentsPerGroup;
	std::vector<Student> students;

	AdaptationConfiguration divideStudents(std::vector<Student> students);
	AdaptationMechanic generateMechanic(LearningProfile bestConfigProfile);
public:
	Adaptation(std::vector<Student> students, int numberOfConfigChoices, int maxNumberOfStudentsPerGroup);
	std::vector<AdaptationMechanic> iterate();

};