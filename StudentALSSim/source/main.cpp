#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

int numRuns = 100;


const int numStudentsInClass = 23;

int numTrainingCycles = 30;
const int numAdaptationCycles = 200;

const int numStudentModelCells = 1;

int numAdaptationConfigurationChoices = 100;
int timeWindow = 30;
int maxNumStudentsPerGroup = 5;
int minNumStudentsPerGroup = 2;

std::ofstream resultsFile("E:/interactions-based-adaptation-for-learning/StudentALSSim/resultsSamples.txt", std::ios::in | std::ios::out);

//define and init globals and utilities
std::vector<Student*> Globals::students = std::vector<Student*>();
int Utilities::defaultRandomSeed = time(NULL);
std::uniform_real_distribution<double> Utilities::uniformDistributionReal = std::uniform_real_distribution<double>();
std::uniform_int_distribution<> Utilities::uniformDistributionInt = std::uniform_int_distribution<>();
std::normal_distribution<double> Utilities::normalDistribution = std::normal_distribution<double>();

void createGlobals(int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell, int numIterations) {
	Utilities::resetRandoms();
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a", numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell, numIterations));
	}
}
void resetGlobals(int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell) {
	//generate all of the students models
	for (int i = 0; i < numStudentsInClass; i++) {
		Student* currStudent = Globals::students[i];
		currStudent->reset(numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell);
	}
}
void destroyGlobals(int numStudentsInClass) {
	for (int i = 0; i < numStudentsInClass; i++) {
		delete Globals::students[i];
	}
}

void simulateStudentsReaction(int numStudentsInClass, int currIteration) {
	//simulate students reaction
	for (int j = 0; j < numStudentsInClass; j++) {
		Student* currStudent = Globals::students[j];
		currStudent->simulateReaction(currIteration);
	}
}


void runAdaptationModule(int numStudentsInClass, int currRun, Adaptation* adapt) {
	int i = 0;
	while (true) {

		/*if (i == 0) {
			break;
		}*/
		printf("\rstep %d of %d of run %d          hui  samples ", i, numAdaptationCycles, currRun);

		AdaptationConfiguration currAdaptedConfig = adapt->getCurrAdaptedConfig();
		std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;
		for (int j = 0; j < groups.size(); j++) {
			adapt->avgPrefDiff[i] += groups[j].avgPreferences.distanceBetween(groups[j].profile) / (groups.size() * numRuns);
		}

		//firstStudentPath.push_back(Globals::students[0]->getCurrProfile());
		for (int j = 0; j < numStudentsInClass; j++) {
			adapt->avgAbilities[i] += Globals::students[j]->currModelIncreases.ability / (numStudentsInClass * numRuns);
			adapt->avgEngagements[i] += Globals::students[j]->currModelIncreases.engagement / (numStudentsInClass * numRuns);
		}

		if (i > (adapt->getNumAdaptationCycles()-1)) {
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
		simulateStudentsReaction(numStudentsInClass, numTrainingCycles + i);

		i++;

	}
}


void trainingPhase(int numStudentsInClass) {
	Adaptation randomClose = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numTrainingCycles);
	runAdaptationModule(numStudentsInClass, 0, &randomClose);
}

void storeSimData(std::string configId, Adaptation adapt) {

	std::vector<int> groupSizeFreqs = adapt.groupSizeFreqs;
	std::vector<int> configSizeFreqs = adapt.configSizeFreqs;

	std::vector<double> avgAbilities = adapt.avgAbilities;
	std::vector<double> avgEngagements = adapt.avgEngagements;
	std::vector<double> avgPrefDiff = adapt.avgPrefDiff;
	double avgExecutionTime = adapt.avgExecutionTime;


	resultsFile << "\ttimesteps=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << i;
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

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

	resultsFile << "\t" << configId.c_str() << "Abilities=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgAbilities[i];
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << "\t" << configId.c_str() << "Engagements=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgEngagements[i];
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n\n";

	resultsFile << "\t" << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgPrefDiff[i];
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << "\t" << configId.c_str() << "groupSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass + 1; i++) {
		resultsFile << groupSizeFreqs[i];
		if (i != numStudentsInClass) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";


	resultsFile << "\t" << configId.c_str() << "configSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass + 1; i++) {
		resultsFile << configSizeFreqs[i];
		if (i != numStudentsInClass) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << "\t" << configId.c_str() << "avgExecTime=" << avgExecutionTime;

	resultsFile << "\n\n";

	resultsFile.flush();
}

int main() {


	//Adaptation randomClose = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numAdaptationCycles);
	//Adaptation optimalClose = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 1, numAdaptationCycles);
	//Adaptation GAL1 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 1, 2, numAdaptationCycles);
	//Adaptation GAL5 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	//Adaptation GAL24 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 24, 2, numAdaptationCycles);
	//Adaptation GAL30 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 30, 2, numAdaptationCycles);
	//for (int i = 0; i < numRuns; i++) {
	//	//resultsFile << "inhPrf =  [" << Globals::students[0]->getInherentPreference().K_cl << "," << Globals::students[0]->getInherentPreference().K_cp << "," << Globals::students[0]->getInherentPreference().K_i << "]";
	//	
	//	createGlobals(numStudentsInClass, numStudentModelCells, timeWindow, numTrainingCycles + numAdaptationCycles);
	//	trainingPhase(numStudentsInClass);
	//	runAdaptationModule(numStudentsInClass, i, &optimalClose);

	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
	//	trainingPhase(numStudentsInClass);
	//	runAdaptationModule(numStudentsInClass, i, &randomClose);

	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
	//	trainingPhase(numStudentsInClass);
	//	runAdaptationModule(numStudentsInClass, i, &GAL1);
	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
	//	trainingPhase(numStudentsInClass);
	//	runAdaptationModule(numStudentsInClass, i, &GAL5);
	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
	//	trainingPhase(numStudentsInClass);
	//	runAdaptationModule(numStudentsInClass, i, &GAL24);
	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
	//	trainingPhase(numStudentsInClass);
	//	runAdaptationModule(numStudentsInClass, i, &GAL30);
	//	resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

	//	destroyGlobals(numStudentsInClass);
	//}

	//storeSimData("randomClose", randomClose);
	//storeSimData("optimalClose", optimalClose);

	//storeSimData("GAL1", GAL1);
	//storeSimData("GAL5", GAL5);
	//storeSimData("GAL24", GAL24);
	//storeSimData("GAL30", GAL30);

	Adaptation randomClose = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numAdaptationCycles);
	Adaptation optimalClose = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 1, numAdaptationCycles);
	Adaptation GAL10 = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	Adaptation GAL100 = Adaptation(numStudentsInClass, 100, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	Adaptation GAL1000 = Adaptation(numStudentsInClass, 1000, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	Adaptation GAL2000 = Adaptation(numStudentsInClass, 2000, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	for (int i = 0; i < numRuns; i++) {

		createGlobals(numStudentsInClass, numStudentModelCells, timeWindow, numTrainingCycles + numAdaptationCycles);
		/*trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &optimalClose);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &randomClose);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);*/
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL10);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL100);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL1000);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL2000);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);

		destroyGlobals(numStudentsInClass);
	}
/*
	storeSimData("randomClose", randomClose);
	storeSimData("optimalClose", optimalClose);*/
	
	storeSimData("GAL10", GAL10);
	storeSimData("GAL100", GAL100);
	storeSimData("GAL1000", GAL1000);
	storeSimData("GAL2000", GAL2000);

	
	resultsFile.close();
	
	return 0;
}

