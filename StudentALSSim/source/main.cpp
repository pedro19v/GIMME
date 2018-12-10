#include "../headers/Sim.h"
#include "../headers/Adaptation.h"
#include "../headers/matplotlibcpp.h"

#include <cmath>

namespace plt = matplotlibcpp;

const int numberOfStudentsInClass = 40;
const int numberOfAdaptationCycles = 10;

int numberOfAdaptationConfigurationChoices = 20;
int maxNumberOfStudentsPerGroup = 10;

void main() {

	std::vector<std::vector<double>> preferences = std::vector<std::vector<double>>(numberOfStudentsInClass);
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		preferences[i] = std::vector<double>(numberOfAdaptationCycles);
	}
	std::vector<double> cycles = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		cycles[i]=i;
	}


	//generate all of the students models
	std::vector<Student> students = std::vector<Student>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		students.push_back(Student(i, "a"));
	}

	Adaptation adapt = Adaptation(students, numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup);

	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		
		//extract adapted mechanics
		std::vector<AdaptationMechanic> mechanics;
		mechanics = adapt.iterate();

		//intervene
		for (int j = 0; j < mechanics.size(); j++) {
			printf("new mechanic: %s", mechanics[j].name.c_str());
		}

		for (int j = 0; j < numberOfStudentsInClass; j++) {
			preferences[j][i] = students[j].getPreference();
		}
		getchar();
	}
	
	plt::plot(cycles, preferences[0]);
	plt::show();
	
}
