#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"
//#include "../headers/matplotlibcpp.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
//
//namespace plt = matplotlibcpp;

const int numberOfStudentsInClass = 25;
const int numberOfAdaptationCycles = 5000;

const int numberOfFitnessNNs = 10;
const int numberOfStudentModelCells = 1;
const int maxAmountOfStoredProfilesPerCell = 20;

int numberOfAdaptationConfigurationChoices = 1000;
int maxNumberOfStudentsPerGroup = 5;


std::ofstream resultsFile("C:/Users/Utilizador/Documents/faculdade/doutoramento/thesis/ThesisMainTool/phdMainToolRep/StudentALSSim/results.txt", std::ios::in | std::ios::out);


//define and init globals and utilities
std::vector<Student*> Globals::students = std::vector<Student*>();
std::default_random_engine Utilities::normalRandomGenerator;

void createGlobals() {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a", numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell));
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
		currStudent->simulateReaction();
	}
}

void trainingPhase() {
	for (int i = 0; i < 20; i++) {
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

void runAdaptationModule(Adaptation adapt, int numberOfAdaptationCycles, std::vector<double> &avgAbilities, std::vector<double> &avgEngagements, std::vector<Utilities::LearningProfile> &firstStudentPath) {
	for (int i = 0; i < numberOfAdaptationCycles; i++) {

		printf("\rstep %d of %d", i, numberOfAdaptationCycles);

		//extract adapted mechanics
		std::vector<AdaptationMechanic> mechanics;
		mechanics = adapt.iterate(Globals::students);
		int mechanicsSize = mechanics.size();
		
		/*resultsFile << "currProfile: " << Globals::students[0]->getCurrProfile().K_cl << Globals::students[0]->getCurrProfile().K_cp << Globals::students[0]->getCurrProfile().K_i << std::endl;
		resultsFile << "ability: " << Globals::students[0]->getAbility() << std::endl;
		resultsFile << "preference: " << Globals::students[0]->getEngagement() << std::endl;*/

		//intervene
		/*for (int j = 0; j < mechanicsSize; j++) {
		printf("new mechanic: %s", mechanics[j].name.c_str());
		}*/
		simulateStudentsReaction();

		firstStudentPath.push_back(Globals::students[0]->getCurrProfile());
		for (int j = 0; j < numberOfStudentsInClass; j++) {
			avgAbilities[i] += Globals::students[j]->getAbility() / numberOfStudentsInClass;
			avgEngagements[i] += Globals::students[j]->getEngagement() / numberOfStudentsInClass;
		}
		std::cout << "avgAb[" << i << "]: " << avgAbilities[i] << std::endl;
		std::cout << "avgEn[" << i <<"]: " << avgEngagements[i] << std::endl;

	}
}


void storeSimData(std::string configId, std::vector<double> &avgAbilities, std::vector<double> &avgEngagements, std::vector<Utilities::LearningProfile> &firstStudentPath) {
	resetGlobals();
	resultsFile << configId.c_str() << "_profileCls=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << firstStudentPath[i].K_cl;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}

	resultsFile << "]\n";
	resultsFile << configId.c_str() << "_profileCps=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << firstStudentPath[i].K_cp;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";
	resultsFile << configId.c_str() << "_profileIs=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << firstStudentPath[i].K_i;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";
	firstStudentPath.clear();

	resultsFile << configId.c_str() << "Abilities=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << avgAbilities[i];
		avgAbilities[i] = 0;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "Engagements=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << avgEngagements[i];
		avgEngagements[i] = 0;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n\n";
	resultsFile.flush();
}

int main() {
	resultsFile << "e";

	std::vector<double> avgAbilities = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgAbilities[i] = 0;
	}
	std::vector<double> avgEngagements = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgEngagements[i] = 0;
	}
	std::vector<Utilities::LearningProfile> firstStudentPath = std::vector<Utilities::LearningProfile>();
	
	std::vector<double> cycles = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		cycles[i]=i;
	}


	//with the adaptation algorithm
	createGlobals();

	/*Adaptation adapt = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, 0);
	trainingPhase();
	runAdaptationModule(adapt, numberOfAdaptationCycles, avgAbilities, avgEngagements, firstStudentPath);
	
	storeSimData("random", avgAbilities, avgEngagements, firstStudentPath);
	
	Adaptation adapt2 = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, 1);
	trainingPhase();
	runAdaptationModule(adapt2, numberOfAdaptationCycles, avgAbilities, avgEngagements, firstStudentPath);

	storeSimData("optimal", avgAbilities, avgEngagements, firstStudentPath);*/

	Adaptation adapt3 = Adaptation(numberOfAdaptationConfigurationChoices, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, 2);
	trainingPhase();
	runAdaptationModule(adapt3, numberOfAdaptationCycles, avgAbilities, avgEngagements, firstStudentPath);

	storeSimData("IAL", avgAbilities, avgEngagements, firstStudentPath);


	resultsFile.close();
	destroyGlobals();
	
	return 0;
}

