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
	int numberOfConfigChoices;
	int maxNumberOfStudentsPerGroup;

	AdaptationConfiguration divideStudents(std::vector<Student*> students);
	AdaptationMechanic generateMechanic(Utilities::LearningProfile bestConfigProfile);
public:
	Adaptation(int numberOfConfigChoices, int maxNumberOfStudentsPerGroup);
	std::vector<AdaptationMechanic> iterate(std::vector<Student*> students);

};