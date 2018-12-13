#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"
#include "../headers/matplotlibcpp.h"

#include <cmath>

namespace plt = matplotlibcpp;

const int numberOfStudentsInClass = 40;
const int numberOfAdaptationCycles = 10;
const int numberOfFitnessNNs = 3;

int numberOfAdaptationConfigurationChoices = 20;
int maxNumberOfStudentsPerGroup = 10;

//define and init globals
std::vector<Student*> Globals::students = std::vector<Student*>();
void initGlobals() {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a"));
	}
}
void destroyGlobals() {
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		delete Globals::students[i];
	}
}

void runAdaptation(Adaptation adapt, std::vector<double> &avgAbilities) {
	for (int i = 0; i < numberOfAdaptationCycles; i++) {

		//extract adapted mechanics
		std::vector<AdaptationMechanic> mechanics;
		mechanics = adapt.iterate(Globals::students);
		int mechanicsSize = mechanics.size();

		//intervene
		/*for (int j = 0; j < mechanicsSize; j++) {
		printf("new mechanic: %s", mechanics[j].name.c_str());
		}*/

		for (int j = 0; j < numberOfStudentsInClass; j++) {
			avgAbilities[i] += Globals::students[j]->getAbility() / numberOfStudentsInClass;
		}

		//simulate students reaction
		for (int j = 0; j < numberOfStudentsInClass; j++) {
			Student* currStudent = Globals::students[j];

			Utilities::LearningProfile currProfile = currStudent->getCurrProfile();
			Utilities::LearningProfile inherentPreference = currStudent->getInherentPreference();

			double onOffTaskSim = currProfile.K_cl*inherentPreference.K_cl + currProfile.K_cp*inherentPreference.K_cp + currProfile.K_i*inherentPreference.K_i;
			currStudent->setPreference(onOffTaskSim);

			double learningRate = currStudent->getLearningRate();
			double abilityIncreaseSim = learningRate * onOffTaskSim;
			currStudent->setAbility(currStudent->getAbility() + abilityIncreaseSim);

			Globals::students[j] = currStudent;
		}

		//getchar();
	}
}

int main() {

	std::vector<double> avgAbilities = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgAbilities[i] = 0;
	}
	std::vector<double> cycles = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		cycles[i]=i;
	}


	//with the adaptation algorithm
	initGlobals();

	Adaptation adapt = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, false);
	runAdaptation(adapt,avgAbilities);

	destroyGlobals();
	plt::plot(cycles, avgAbilities);

	initGlobals();

	adapt = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, true);
	runAdaptation(adapt, avgAbilities);

	destroyGlobals();
	plt::plot( cycles, avgAbilities);
	plt::show();
	
	return 0;
}
