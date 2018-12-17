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

const int numberOfFitnessNNs = 10;
const int maxAmountOfStoredProfiles = 20;

int numberOfAdaptationConfigurationChoices = 5000;
int maxNumberOfStudentsPerGroup = 5;


std::ofstream resultsFile;


//define and init globals
std::vector<Student*> Globals::students = std::vector<Student*>();
void createGlobals() {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a", maxAmountOfStoredProfiles));
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

void simulateStudentsReaction() {
	//simulate students reaction
	for (int j = 0; j < numberOfStudentsInClass; j++) {
		Student* currStudent = Globals::students[j];
		currStudent->simulateReaction(numberOfAdaptationCycles);
	}
}

void trainingPhase() {
	for (int i = 0; i < maxAmountOfStoredProfiles; i++) {
		//simulate students reaction
		for (int j = 0; j < numberOfStudentsInClass; j++) {
			Student* currStudent = Globals::students[j];
			if (i % 3 == 0) {
				currStudent->changeCurrProfile(Utilities::LearningProfile{ 1,0,0 });
			}
			else if (i % 3 == 1) {
				currStudent->changeCurrProfile(Utilities::LearningProfile{ 0,1,0 });
			}
			else if (i % 3 == 2) {
				currStudent->changeCurrProfile(Utilities::LearningProfile{ 0,0,1 });
			}

			simulateStudentsReaction();
		}
	}
}

void runAdaptationModule(Adaptation adapt, int numberOfAdaptationCycles, std::vector<double> &avgAbilities) {
	for (int i = 0; i < numberOfAdaptationCycles; i++) {

		printf("\rstep %d of %d", i, numberOfAdaptationCycles);

		//extract adapted mechanics
		std::vector<AdaptationMechanic> mechanics;
		mechanics = adapt.iterate(Globals::students);
		int mechanicsSize = mechanics.size();
		
		resultsFile << "currProfile: " << Globals::students[0]->getCurrProfile().K_cl << Globals::students[0]->getCurrProfile().K_cp << Globals::students[0]->getCurrProfile().K_i << std::endl;
		resultsFile << "ability: " << Globals::students[0]->getAbility() << std::endl;
		resultsFile << "preference: " << Globals::students[0]->getPreference() << std::endl;

		//intervene
		/*for (int j = 0; j < mechanicsSize; j++) {
		printf("new mechanic: %s", mechanics[j].name.c_str());
		}*/
		simulateStudentsReaction();

		for (int j = 0; j < numberOfStudentsInClass; j++) {
			avgAbilities[i] += Globals::students[j]->getAbility() / numberOfStudentsInClass;
		}
		std::cout << "avgAb[" << i <<"]: " << avgAbilities[i] << std::endl;

	}
}


int main() {

	resultsFile.open("./results.txt");
	resultsFile << "d";

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
	runAdaptationModule(adapt, numberOfAdaptationCycles, avgAbilities);
	
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
	runAdaptationModule(adapt, numberOfAdaptationCycles, avgAbilities);

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

