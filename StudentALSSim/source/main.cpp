#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

int numRuns = 30;


const int numStudentsInClass = 25;

int numTrainingCycles = 18;
const int numAdaptationCycles = 200;

const int numStudentModelCells = 1;

int numAdaptationConfigurationChoices = 100;
int timeWindow = 30;
int maxNumStudentsPerGroup = 5;
int minNumStudentsPerGroup = 2;

std::ofstream resultsFile("C:/Users/Utilizador/Documents/faculdade/doutoramento/thesis/ThesisMainTool/phdMainToolRep/StudentALSSim/results.txt", std::ios::in | std::ios::out);

//define and init globals and utilities
std::vector<Student*> Globals::students = std::vector<Student*>();
int Utilities::defaultRandomSeed = time(NULL);
std::uniform_real_distribution<double> Utilities::uniformDistributionReal = std::uniform_real_distribution<double>();
std::uniform_int_distribution<> Utilities::uniformDistributionInt = std::uniform_int_distribution<>();
std::normal_distribution<double> Utilities::normalDistribution = std::normal_distribution<double>();

void createGlobals(int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell, int numIterations) {
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
	Utilities::resetRandoms();
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

void trainingPhase(int numStudentsInClass) {
	for (int i = 0; i < numTrainingCycles; i++) {
		//simulate students reaction
		for (int j = 0; j < numStudentsInClass; j++) {
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

		simulateStudentsReaction(numStudentsInClass,i);
	}
}

void runAdaptationModule(int numStudentsInClass, int currRun, Adaptation* adapt) {
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
		for (int j = 0; j < numStudentsInClass; j++) {
			adapt->avgAbilities[i] += Globals::students[j]->getAbility() / (numStudentsInClass * numRuns);
			adapt->avgEngagements[i] += Globals::students[j]->getEngagement() / (numStudentsInClass * numRuns);
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
		simulateStudentsReaction(numStudentsInClass, numTrainingCycles + i);

		i++;

	}
}


void storeSimData(std::string configId, Adaptation adapt) {

	std::vector<int> groupSizeFreqs = adapt.groupSizeFreqs;
	std::vector<int> configSizeFreqs = adapt.configSizeFreqs;

	std::vector<double> avgAbilities = adapt.avgAbilities;
	std::vector<double> avgEngagements = adapt.avgEngagements;
	std::vector<double> avgPrefDiff = adapt.avgPrefDiff;
	double avgExecutionTime = adapt.avgExecutionTime;


	resultsFile << "timesteps=[";
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

	resultsFile << configId.c_str() << "Abilities=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgAbilities[i];
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "Engagements=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgEngagements[i];
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n\n";

	resultsFile << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		resultsFile << avgPrefDiff[i];
		if (i != (numAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "groupSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass; i++) {
		resultsFile << groupSizeFreqs[i];
		if (i != (numStudentsInClass - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";


	resultsFile << configId.c_str() << "configSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass; i++) {
		resultsFile << configSizeFreqs[i];
		if (i != (numStudentsInClass - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n";

	resultsFile << configId.c_str() << "avgExecTime=" << avgExecutionTime;

	resultsFile << "\n\n";

	resultsFile.flush();
}

int main() {


	Adaptation randomClose = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numAdaptationCycles);
	Adaptation optimalClose = Adaptation(numStudentsInClass, 1000, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 1, numAdaptationCycles);
	Adaptation GAL1 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 1, 2, numAdaptationCycles);
	Adaptation GAL2 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 2, 2, numAdaptationCycles);
	Adaptation GAL3 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 3, 2, numAdaptationCycles);
	Adaptation GAL4 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 4, 2, numAdaptationCycles);
	Adaptation GAL5 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles);
	Adaptation GAL6 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 6, 2, numAdaptationCycles);
	Adaptation GAL7 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 7, 2, numAdaptationCycles);
	Adaptation GAL8 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 8, 2, numAdaptationCycles);
	Adaptation GAL9 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 9, 2, numAdaptationCycles);
	Adaptation GAL10 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 10, 2, numAdaptationCycles);
	Adaptation GAL12 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 12, 2, numAdaptationCycles);
	Adaptation GAL16 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 16, 2, numAdaptationCycles);
	Adaptation GAL20 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 20, 2, numAdaptationCycles);
	Adaptation GAL24 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 24, 2, numAdaptationCycles);
	Adaptation GAL28 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 28, 2, numAdaptationCycles);
	Adaptation GAL30 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 30, 2, numAdaptationCycles);
	for (int i = 0; i < numRuns; i++) {
		//resultsFile << "inhPrf =  [" << Globals::students[0]->getInherentPreference().K_cl << "," << Globals::students[0]->getInherentPreference().K_cp << "," << Globals::students[0]->getInherentPreference().K_i << "]";
		
		createGlobals(numStudentsInClass, numStudentModelCells, timeWindow, numTrainingCycles + numAdaptationCycles);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &optimalClose);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &randomClose);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL1);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL2);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL4);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL8);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL12);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL16);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL20);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL24);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL28);
		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL30);

	}

	storeSimData("randomClose", randomClose);
	storeSimData("optimalClose", optimalClose);
	
	storeSimData("GAL1", GAL1);
	storeSimData("GAL2", GAL2);
	storeSimData("GAL4", GAL4);
	storeSimData("GAL8", GAL8);
	storeSimData("GAL12", GAL12);
	storeSimData("GAL16", GAL16);
	storeSimData("GAL20", GAL20);
	storeSimData("GAL24", GAL24);
	storeSimData("GAL28", GAL28);
	storeSimData("GAL30", GAL30);

	
	resultsFile.close();
	
	return 0;
}

