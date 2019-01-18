#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

int numRuns = 2;


const int numberOfStudentsInClass = 25;
const int numberOfAdaptationCycles = 200;

const int numberOfStudentModelCells = 1;

int numberOfAdaptationConfigurationChoices = 100;
int maxNumberOfStudentsPerGroup = 10;
int minNumberOfStudentsPerGroup = 2;

std::ofstream resultsFile("C:/Users/Utilizador/Documents/faculdade/doutoramento/thesis/ThesisMainTool/phdMainToolRep/StudentALSSim/results.txt", std::ios::in | std::ios::out);



//define and init globals and utilities
std::vector<Student*> Globals::students = std::vector<Student*>();

void createGlobals(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell) {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a", numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell));
	}
}
void resetGlobals(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell) {
	//generate all of the students models
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Student* currStudent = Globals::students[i];
		currStudent->reset(numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell);
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
	for (int i = 0; i < 18; i++) {
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
		}

		simulateStudentsReaction();
	}
}

void runAdaptationModule(int currRun, Adaptation* adapt) {
	int i = 0;
	while (true) {

		/*if (i == 0) {
			break;
		}*/
		printf("\rstep %d of %d of run %d              ", i, numberOfAdaptationCycles, currRun);

		AdaptationConfiguration currAdaptedConfig = adapt->getCurrAdaptedConfig();
		std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;
		for (int j = 0; j < groups.size(); j++) {
			adapt->avgPrefDiff[i] += groups[j].avgPreferences.distanceBetween(groups[j].profile) / (groups.size() * numRuns);
		}

		//firstStudentPath.push_back(Globals::students[0]->getCurrProfile());
		for (int j = 0; j < numberOfStudentsInClass; j++) {
			adapt->avgAbilities[i] += Globals::students[j]->getAbility() / (numberOfStudentsInClass * numRuns);
			adapt->avgEngagements[i] += Globals::students[j]->getEngagement() / (numberOfStudentsInClass * numRuns);
		}

		if (i > (numberOfAdaptationCycles-1)) {
			break;
		}

		//extract adapted mechanics
		std::vector<AdaptationMechanic> mechanics;

		const clock_t beginTime = clock();
		mechanics = adapt->iterate(Globals::students);
		adapt->avgExecutionTime += (float(clock() - beginTime) / CLOCKS_PER_SEC) / (numberOfAdaptationCycles*numRuns);

		int mechanicsSize = mechanics.size();
		
		/*resultsFile << "currProfile: " << Globals::students[0]->getCurrProfile().K_cl << Globals::students[0]->getCurrProfile().K_cp << Globals::students[0]->getCurrProfile().K_i << std::endl;
		resultsFile << "ability: " << Globals::students[0]->getAbility() << std::endl;
		resultsFile << "preference: " << Globals::students[0]->getEngagement() << std::endl;*/

		//intervene
		/*for (int j = 0; j < mechanicsSize; j++) {
		printf("new mechanic: %s", mechanics[j].name.c_str());
		}*/
		simulateStudentsReaction();

		i++;

	}
}


void storeSimData(std::string configId, Adaptation adapt) {

	std::vector<double> avgAbilities = adapt.avgAbilities;
	std::vector<double> avgEngagements = adapt.avgEngagements;
	std::vector<double> avgPrefDiff = adapt.avgPrefDiff;
	double avgExecutionTime = adapt.avgExecutionTime;

	/*resultsFile << configId.c_str() << "_profileCls=[";
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
	firstStudentPath.clear();*/

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

	resultsFile << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << avgPrefDiff[i];
		avgPrefDiff[i] = 0;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "avgExecTime=" << avgExecutionTime;

	resultsFile << "\n\n";

	resultsFile.flush();
}

int main() {
	//set default random seed
	Utilities::defaultRandomSeed = time(NULL);


	Adaptation randomClose = Adaptation(10, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 5, 0, numberOfAdaptationCycles);
	Adaptation optimalClose = Adaptation(10000, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 5, 1, numberOfAdaptationCycles);
	Adaptation GAL1 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 1, 2, numberOfAdaptationCycles);
	Adaptation GAL2 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 2, 2, numberOfAdaptationCycles);
	Adaptation GAL3 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 3, 2, numberOfAdaptationCycles);
	Adaptation GAL4 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 4, 2, numberOfAdaptationCycles);
	Adaptation GAL5 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 5, 2, numberOfAdaptationCycles);
	Adaptation GAL6 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 6, 2, numberOfAdaptationCycles);
	Adaptation GAL7 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 7, 2, numberOfAdaptationCycles);
	Adaptation GAL8 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 8, 2, numberOfAdaptationCycles);
	Adaptation GAL9 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 9, 2, numberOfAdaptationCycles);
	Adaptation GAL10 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, 10, 2, numberOfAdaptationCycles);
	for (int i = 0; i < numRuns; i++) {
		//resultsFile << "inhPrf =  [" << Globals::students[0]->getInherentPreference().K_cl << "," << Globals::students[0]->getInherentPreference().K_cp << "," << Globals::students[0]->getInherentPreference().K_i << "]";
		
		createGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &optimalClose);

		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &randomClose);

		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL1);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL2);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL3);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL4);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL5);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL6);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL7);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL8);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL9);
		resetGlobals(numberOfStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL10);
	}

	storeSimData("randomClose", randomClose);
	storeSimData("optimalClose", optimalClose);
	
	storeSimData("GAL1", GAL1);
	storeSimData("GAL2", GAL2);
	storeSimData("GAL3", GAL3);
	storeSimData("GAL4", GAL4);
	storeSimData("GAL5", GAL5);
	storeSimData("GAL6", GAL6);
	storeSimData("GAL7", GAL7);
	storeSimData("GAL8", GAL8);
	storeSimData("GAL9", GAL9);
	storeSimData("GAL10", GAL10);


	
	resultsFile.close();
	
	return 0;
}

