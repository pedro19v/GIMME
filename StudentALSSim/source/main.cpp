#include "../headers/Globals.h"
#include "../headers/Utilities.h"
#include "../headers/Adaptation.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <ios>
#include <string>

int numRuns = 1;


const int numStudentsInClass = 25;

int numTrainingCycles = 18;
const int numAdaptationCycles = 20;

const int numStudentModelCells = 1;

int numAdaptationConfigurationChoices = 100;
int timeWindow = 30;
int maxNumStudentsPerGroup = 5;
int minNumStudentsPerGroup = 2;

int numTasksPerGroup = 3;

std::ofstream statisticsFile("C:/Users/Utilizador/Documents/faculdade/doutoramento/thesis/ThesisMainTool/phdMainToolRep/StudentALSSim/statistics.txt", std::ios::in | std::ios::out);
std::ofstream resultsFile("C:/Users/Utilizador/Documents/faculdade/doutoramento/thesis/ThesisMainTool/phdMainToolRep/StudentALSSim/results.txt", std::ios::in | std::ios::out);

//define and init globals and utilities
std::vector<Student*> Globals::students = std::vector<Student*>();
int Utilities::defaultRandomSeed = time(NULL);
std::uniform_real_distribution<double> Utilities::uniformDistributionReal = std::uniform_real_distribution<double>();
std::uniform_int_distribution<> Utilities::uniformDistributionInt = std::uniform_int_distribution<>();
std::normal_distribution<double> Utilities::normalDistribution = std::normal_distribution<double>();

std::vector<AdaptationTask> Globals::possibleCollaborativeTasks = std::vector<AdaptationTask>();
std::vector<AdaptationTask> Globals::possibleCompetitiveTasks = std::vector<AdaptationTask>();
std::vector<AdaptationTask> Globals::possibleIndividualTasks = std::vector<AdaptationTask>();

void createGlobals(int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell, int numIterations) {
	//generate all of the students models
	Globals::students = std::vector<Student*>();
	for (int i = 0; i < numStudentsInClass; i++) {
		Globals::students.push_back(new Student(i, "a", numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell, numIterations));
	}

	Globals::possibleCollaborativeTasks = std::vector<AdaptationTask>();
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab1" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab2" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab3" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab4" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab5" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab6" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab7" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab8" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab9" });
	Globals::possibleCollaborativeTasks.push_back({ AdaptationTaskType::COLLABORATION,"collab10" });

	Globals::possibleCompetitiveTasks = std::vector<AdaptationTask>();
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp1" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp2" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp3" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp4" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp5" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp6" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp7" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp8" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp9" });
	Globals::possibleCompetitiveTasks.push_back({ AdaptationTaskType::COMPETITION,"comp10" });

	Globals::possibleIndividualTasks = std::vector<AdaptationTask>();
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self1" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self2" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self3" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self4" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self5" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self6" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self7" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self8" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self9" });
	Globals::possibleIndividualTasks.push_back({ AdaptationTaskType::SELF_INTERACTION,"self10" });
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
		std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> groupMechanicPairs;

		const clock_t beginTime = clock();
		groupMechanicPairs = adapt->iterate(Globals::students, Globals::possibleCollaborativeTasks, Globals::possibleCompetitiveTasks, Globals::possibleIndividualTasks, numTrainingCycles + i);
		adapt->avgExecutionTime += (float(clock() - beginTime) / CLOCKS_PER_SEC) / (numAdaptationCycles*numRuns);

		int mechanicsSize = groupMechanicPairs.size();
		
		/*statisticsFile << "currProfile: " << Globals::students[0]->getCurrProfile().K_cl << Globals::students[0]->getCurrProfile().K_cp << Globals::students[0]->getCurrProfile().K_i << std::endl;
		statisticsFile << "ability: " << Globals::students[0]->getAbility() << std::endl;
		statisticsFile << "preference: " << Globals::students[0]->getEngagement() << std::endl;*/

		//intervene
		for (int j = 0; j < mechanicsSize; j++) {

			std::vector<Student*> currGroup = groupMechanicPairs[j].first.students;
			std::vector<AdaptationTask> currMechanic = groupMechanicPairs[j].second;

			resultsFile << "promote on students:" << std::endl;
			for (int k = 0; k < currGroup.size(); k++) {
				resultsFile << "Number: " << currGroup[k]->getId() << ", Name: " << currGroup[k]->getName()  << std::endl;
			}
			resultsFile << ", the following tasks:" << std::endl;
			for (int k = 0; k < currMechanic.size(); k++) {
				resultsFile << currMechanic[k].description << std::endl;
			}
			resultsFile << "-- -- -- -- -- -- -- -- -- -- -- -- --" << std::endl;
		}
		resultsFile << "----------------------End of Iteration--------------------" << std::endl;
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


	statisticsFile << "timesteps=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		statisticsFile << i;
		if (i != (numAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";

	/*statisticsFile << configId.c_str() << "_profileCls=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		statisticsFile << firstStudentPath[i].K_cl;
		if (i != (numberOfAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}

	statisticsFile << "]\n";
	statisticsFile << configId.c_str() << "_profileCps=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		statisticsFile << firstStudentPath[i].K_cp;
		if (i != (numberOfAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";
	statisticsFile << configId.c_str() << "_profileIs=[";
	for (int i = 0; i < numberOfAdaptationCycles; i++) {
		statisticsFile << firstStudentPath[i].K_i;
		if (i != (numberOfAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";
	firstStudentPath.clear();*/

	statisticsFile << configId.c_str() << "Abilities=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		statisticsFile << avgAbilities[i];
		if (i != (numAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";

	statisticsFile << configId.c_str() << "Engagements=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		statisticsFile << avgEngagements[i];
		if (i != (numAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n\n";

	statisticsFile << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		statisticsFile << avgPrefDiff[i];
		if (i != (numAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";

	statisticsFile << configId.c_str() << "groupSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass; i++) {
		statisticsFile << groupSizeFreqs[i];
		if (i != (numStudentsInClass - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";


	statisticsFile << configId.c_str() << "configSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass; i++) {
		statisticsFile << configSizeFreqs[i];
		if (i != (numStudentsInClass - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";

	statisticsFile << configId.c_str() << "avgExecTime=" << avgExecutionTime;

	statisticsFile << "\n\n";

	statisticsFile.flush();
}

int main() {


	Adaptation randomClose = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numAdaptationCycles, numTasksPerGroup);
	Adaptation optimalClose = Adaptation(numStudentsInClass, 1000, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 1, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL1 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 1, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL2 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 2, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL3 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 3, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL4 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 4, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL5 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL6 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 6, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL7 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 7, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL8 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 8, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL9 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 9, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL10 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 10, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL12 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 12, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL16 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 16, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL20 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 20, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL24 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 24, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL28 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 28, 2, numAdaptationCycles, numTasksPerGroup);
	Adaptation GAL30 = Adaptation(numStudentsInClass, numAdaptationConfigurationChoices, minNumStudentsPerGroup, maxNumStudentsPerGroup, 30, 2, numAdaptationCycles, numTasksPerGroup);
	for (int i = 0; i < numRuns; i++) {
		//statisticsFile << "inhPrf =  [" << Globals::students[0]->getInherentPreference().K_cl << "," << Globals::students[0]->getInherentPreference().K_cp << "," << Globals::students[0]->getInherentPreference().K_i << "]";
		
		/*createGlobals(numStudentsInClass, numStudentModelCells, timeWindow, numTrainingCycles + numAdaptationCycles);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &optimalClose);

		resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &randomClose);
*/
		/*resetGlobals(numStudentsInClass, numStudentModelCells, timeWindow);
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
		runAdaptationModule(numStudentsInClass, i, &GAL30);*/

		createGlobals(numStudentsInClass, numStudentModelCells, timeWindow, numTrainingCycles + numAdaptationCycles);
		trainingPhase(numStudentsInClass);
		runAdaptationModule(numStudentsInClass, i, &GAL5);

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

	
	statisticsFile.close();
	
	return 0;
}

