#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

int numRuns = 50;


const int numberOfStudentsInClass = 25;
const int numberOfAdaptationCycles = 200;

const int numberOfFitnessNNs = 3;
const int numberOfStudentModelCells = 1;
const int maxAmountOfStoredProfilesPerCell = 100;

int numberOfAdaptationConfigurationChoices = 1000;
int maxNumberOfStudentsPerGroup = 5;
int minNumberOfStudentsPerGroup = 2;

std::ofstream resultsFile("E:/interactions-based-adaptation-for-learning/StudentALSSim/results.txt", std::ios::in | std::ios::out);



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

void runAdaptationModule(int currRun, Adaptation adapt, int numberOfAdaptationCycles, 
	std::vector<double> &avgAbilities, std::vector<double> &avgEngagements, std::vector<double> &avgPrefDiff, 
	std::vector<Utilities::LearningProfile> &firstStudentPath) {
	for (int i = 0; i < numberOfAdaptationCycles; i++) {

		printf("\rstep %d of %d of run %d              ", i, numberOfAdaptationCycles, currRun);

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

		AdaptationConfiguration currAdaptedConfig = adapt.getCurrAdaptedConfig();
		std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;
		for (int j = 0; j < groups.size(); j++) {
			avgPrefDiff[i] += groups[j].avgPreferences.distanceBetween(groups[j].profile) / (groups.size() * numRuns);
		}

		firstStudentPath.push_back(Globals::students[0]->getCurrProfile());
		for (int j = 0; j < numberOfStudentsInClass; j++) {
			avgAbilities[i] += Globals::students[j]->getAbility() / (numberOfStudentsInClass * numRuns);
			avgEngagements[i] += Globals::students[j]->getEngagement() / (numberOfStudentsInClass * numRuns);
		}

	}
}


void storeSimData(std::string configId, 
	std::vector<double> &avgAbilities, std::vector<double> &avgEngagements, std::vector<double> &avgPrefDiff,
	std::vector<Utilities::LearningProfile> &firstStudentPath) {

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

	resultsFile << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		resultsFile << avgPrefDiff[i];
		avgPrefDiff[i] = 0;
		if (i != (numberOfAdaptationCycles - 1)) {
			resultsFile << ",";
		}
	}
	resultsFile << "]\n\n";
	resultsFile.flush();
}

int main() {
	
	std::vector<double> avgAbilitiesRandom = std::vector<double>(numberOfAdaptationCycles);
	std::vector<double> avgAbilitiesOptimal = std::vector<double>(numberOfAdaptationCycles);
	std::vector<double> avgAbilitiesGAL = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgAbilitiesRandom[i] = 0;
		avgAbilitiesOptimal[i] = 0;
		avgAbilitiesGAL[i] = 0;
	}
	std::vector<double> avgEngagementsRandom = std::vector<double>(numberOfAdaptationCycles);
	std::vector<double> avgEngagementsOptimal = std::vector<double>(numberOfAdaptationCycles);
	std::vector<double> avgEngagementsGAL = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgEngagementsRandom[i] = 0;
		avgEngagementsOptimal[i] = 0;
		avgEngagementsGAL[i] = 0;
	}
	std::vector<double> avgPrefDiffRandom = std::vector<double>(numberOfAdaptationCycles);
	std::vector<double> avgPrefDiffOptimal = std::vector<double>(numberOfAdaptationCycles);
	std::vector<double> avgPrefDiffGAL = std::vector<double>(numberOfAdaptationCycles);
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		avgPrefDiffRandom[i] = 0;
		avgPrefDiffOptimal[i] = 0;
		avgPrefDiffGAL[i] = 0;
	}
	

	std::vector<Utilities::LearningProfile> firstStudentPathRandom = std::vector<Utilities::LearningProfile>();
	std::vector<Utilities::LearningProfile> firstStudentPathOptimal = std::vector<Utilities::LearningProfile>();
	std::vector<Utilities::LearningProfile> firstStudentPathGAL = std::vector<Utilities::LearningProfile>();
	
	for (int i = 0; i < numRuns; i++) {

		//with the adaptation algorithm
		createGlobals();

		resultsFile << "inhPrf =  [" << Globals::students[0]->getInherentPreference().K_cl << "," << Globals::students[0]->getInherentPreference().K_cp << "," << Globals::students[0]->getInherentPreference().K_i << "]";
	
/*
		Adaptation adapt = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, 0);
		trainingPhase();
		runAdaptationModule(i, adapt, numberOfAdaptationCycles, avgAbilitiesRandom, avgEngagementsRandom, avgPrefDiffRandom, firstStudentPathRandom);

		resetGlobals();

		Adaptation adapt2 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, 1);
		trainingPhase();
		runAdaptationModule(i, adapt2, numberOfAdaptationCycles, avgAbilitiesOptimal, avgEngagementsOptimal, avgPrefDiffOptimal, firstStudentPathOptimal);

		resetGlobals();*/

		Adaptation adapt3 = Adaptation(numberOfAdaptationConfigurationChoices, minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup, numberOfFitnessNNs, 2);
		trainingPhase();
		runAdaptationModule(i, adapt3, numberOfAdaptationCycles, avgAbilitiesGAL, avgEngagementsGAL, avgPrefDiffGAL, firstStudentPathGAL);


		destroyGlobals();

	}

		
	storeSimData("random" + std::to_string(maxAmountOfStoredProfilesPerCell), avgAbilitiesRandom, avgEngagementsRandom, avgPrefDiffRandom, firstStudentPathRandom);
	storeSimData("optimal" + std::to_string(maxAmountOfStoredProfilesPerCell), avgAbilitiesOptimal, avgEngagementsOptimal, avgPrefDiffOptimal, firstStudentPathOptimal);
	storeSimData("GAL" + std::to_string(maxAmountOfStoredProfilesPerCell), avgAbilitiesGAL, avgEngagementsGAL, avgPrefDiffGAL, firstStudentPathGAL);


	
	resultsFile.close();
	
	return 0;
}

