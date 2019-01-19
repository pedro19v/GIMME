#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

int numRuns = 20;


const int numberOfStudentsInClass = 25;

int numTrainingCycles = 18;
const int numAdaptationCycles = 200;

const int numStudentModelCells = 1;

int numAdaptationConfigurationChoices = 100;
int maxNumStudentsPerGroup = 10;
int minNumStudentsPerGroup = 2;

std::ofstream resultsFile("C:/Users/Utilizador/Documents/faculdade/doutoramento/thesis/ThesisMainTool/phdMainToolRep/StudentALSSim/results.txt", std::ios::in | std::ios::out);

//define and init globals and utilities
std::vector<Student*> Globals::students = std::vector<Student*>();
int Utilities::defaultRandomSeed = time(NULL);
std::uniform_real_distribution<double> Utilities::uniformDistribution = std::uniform_real_distribution<double>();
std::normal_distribution<double> Utilities::normalDistribution = std::normal_distribution<double>();

void createGlobals(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell, int numIterations) {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a", numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell, numIterations));
	}
}
void resetGlobals(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell) {
	//generate all of the students models
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		Student* currStudent = Globals::students[i];
		currStudent->reset(numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell);
	}
	Utilities::resetRandoms();
}
void destroyGlobals() {
	for (int i = 0; i < numberOfStudentsInClass; i++) {
		delete Globals::students[i];
	}
}

void simulateStudentsReaction(int currIteration) {
	//simulate students reaction
	for (int j = 0; j < numberOfStudentsInClass; j++) {
		Student* currStudent = Globals::students[j];
		currStudent->simulateReaction(currIteration);
	}
}

void trainingPhase() {
	for (int i = 0; i < numTrainingCycles; i++) {
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

		simulateStudentsReaction(i);
	}
}

void runAdaptationModule(int currRun, Adaptation* adapt) {
	int i = 0;
	while (true) {

		/*if (i == 0) {
			break;
		}*/
		printf("\rstep %d of %d of run %d              ", i, numAdaptationCycles, currRun);

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

		if (i > (numAdaptationCycles-1)) {
			break;
		}

		//extract adapted mechanics
		std::vector<AdaptationMechanic> mechanics;

		const clock_t beginTime = clock();
		mechanics = adapt->iterate(Globals::students, numTrainingCycles + i);
		adapt->avgExecutionTime += (float(clock() - beginTime) / CLOCKS_PER_SEC) / (numAdaptationCycles*numRuns);

		int mechanicsSize = mechanics.size();
		
		/*resultsFile << "currProfile: " << Globals::students[0]->getCurrProfile().K_cl << Globals::students[0]->getCurrProfile().K_cp << Globals::students[0]->getCurrProfile().K_i << std::endl;
		resultsFile << "ability: " << Globals::students[0]->getAbility() << std::endl;
		resultsFile << "preference: " << Globals::students[0]->getEngagement() << std::endl;*/

		//intervene
		/*for (int j = 0; j < mechanicsSize; j++) {
		printf("new mechanic: %s", mechanics[j].name.c_str());
		}*/
		simulateStudentsReaction(numTrainingCycles + i);

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
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgAbilities[i];
		avgAbilities[i] = 0;
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "Engagements=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgEngagements[i];
		avgEngagements[i] = 0;
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n\n";

	resultsFile << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgPrefDiff[i];
		avgPrefDiff[i] = 0;
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "avgExecTime=" << avgExecutionTime;

	resultsFile << "\n\n";

	resultsFile.flush();
}

int main() {


	Adaptation randomClose = Adaptation(10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numAdaptationCycles);
	Adaptation optimalClose = Adaptation(1000, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 1, numAdaptationCycles);
	Adaptation GAL1 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 1, 2, numAdaptationCycles);
	Adaptation GAL2 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 2, 2, numAdaptationCycles);
	Adaptation GAL3 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 3, 2, numAdaptationCycles);
	Adaptation GAL4 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 4, 2, numAdaptationCycles);
	Adaptation GAL5 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	Adaptation GAL6 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 6, 2, numAdaptationCycles);
	Adaptation GAL7 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 7, 2, numAdaptationCycles);
	Adaptation GAL8 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 8, 2, numAdaptationCycles);
	Adaptation GAL9 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 9, 2, numAdaptationCycles);
	Adaptation GAL10 = Adaptation(numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 10, 2, numAdaptationCycles);
	for (int i = 0; i < numRuns; i++) {
		//resultsFile << "inhPrf =  [" << Globals::students[0]->getInherentPreference().K_cl << "," << Globals::students[0]->getInherentPreference().K_cp << "," << Globals::students[0]->getInherentPreference().K_i << "]";
		
		createGlobals(numStudentModelCells, 10, numTrainingCycles + numAdaptationCycles);
		trainingPhase();
		runAdaptationModule(i, &optimalClose);

		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &randomClose);

		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL1);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL2);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL3);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL4);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL5);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL6);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL7);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL8);
		resetGlobals(numStudentModelCells, 10);
		trainingPhase();
		runAdaptationModule(i, &GAL9);
		resetGlobals(numStudentModelCells, 10);
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

