#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"
//#include "../headers/matplotlibcpp.h"

#include <cmath>
#include <iostream>
#include <fstream>
//
//namespace plt = matplotlibcpp;

const int numberOfStudentsInClass = 25;
const int numberOfAdaptationCycles = 1000;
const int numberOfFitnessNNs = 20;

int numberOfAdaptationConfigurationChoices = 500;
int maxNumberOfStudentsPerGroup = 10;

//define and init globals
std::vector<Student*> Globals::students = std::vector<Student*>();
void createGlobals() {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a"));
	}
}
void resetGlobals() {
	//generate all of the students models
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students[i]->reset();
	}
}
void destroyGlobals() {
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		delete Globals::students[i];
	}
}
void trainingPhase() {
	for (int i = 0; i < 30; i++) {

		//simulate students reaction
		for (int j = 0; j < numberOfStudentsInClass; j++) {
			Student* currStudent = Globals::students[j];
			if (i < 10) {
				currStudent->changeCurrProfile(Utilities::LearningProfile{ 1,0,0 });
			}
			else if (i >= 10 && i < 20) {
				currStudent->changeCurrProfile(Utilities::LearningProfile{ 0,1,0 });
			}
			else if (i >= 20 && i < 30) {
				currStudent->changeCurrProfile(Utilities::LearningProfile{ 0,0,1 });
			}

			Utilities::LearningProfile currProfile = currStudent->getCurrProfile();
			Utilities::LearningProfile inherentPreference = currStudent->getInherentPreference();

			double taskTotalTime = 100;

			double onOffTaskSim = currProfile.K_cl*inherentPreference.K_cl*taskTotalTime
				+ currProfile.K_cp*inherentPreference.K_cp*taskTotalTime
				+ currProfile.K_i*inherentPreference.K_i*taskTotalTime;
			currStudent->setPreference(onOffTaskSim);

			double learningRate = currStudent->getLearningRate();
			double abilityIncreaseSim = learningRate * onOffTaskSim;
			currStudent->setAbility(currStudent->getAbility() + abilityIncreaseSim);

			Globals::students[j] = currStudent;
		}
	}
}

void runSystem(Adaptation adapt, int numberOfAdaptationCycles, std::vector<double> &avgAbilities) {
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

			double taskTotalTime = 100;

			double onOffTaskSim = currProfile.K_cl*inherentPreference.K_cl*taskTotalTime 
				+ currProfile.K_cp*inherentPreference.K_cp*taskTotalTime 
				+ currProfile.K_i*inherentPreference.K_i*taskTotalTime;
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

	std::ofstream resultsFile;
	resultsFile.open("./results.txt");
	resultsFile << "b";

	std::vector<double> avgAbilities = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgAbilities[i] = 0;
	}
	std::vector<double> cycles = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		cycles[i]=i;
	}


	//with the adaptation algorithm
	createGlobals();

	Adaptation adapt = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, true);
	trainingPhase();
	runSystem(adapt, numberOfAdaptationCycles, avgAbilities);
	
	resetGlobals();
	resultsFile << "	y1=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << avgAbilities[i];
		avgAbilities[i] = 0;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n\n";

	adapt = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, false);
	trainingPhase();
	runSystem(adapt, numberOfAdaptationCycles, avgAbilities);

	resetGlobals();
	resultsFile << "	y2=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << avgAbilities[i];
		avgAbilities[i] = 0;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]";
	resultsFile.flush();
	resultsFile.close();

	destroyGlobals();

	
	return 0;
}

