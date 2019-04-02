#include "../headers/Core.h"



Core::Core(int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell, int numIterations,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks){
	//define and init globals and utilities
	std::vector<Student*> students = std::vector<Student*>();


	std::vector<AdaptationTask> possibleCollaborativeTasks = std::vector<AdaptationTask>();
	std::vector<AdaptationTask> possibleCompetitiveTasks = std::vector<AdaptationTask>();
	std::vector<AdaptationTask> possibleIndividualTasks = std::vector<AdaptationTask>();


	possibleCollaborativeTasks = std::vector<AdaptationTask>();
	possibleCompetitiveTasks = std::vector<AdaptationTask>();
	possibleIndividualTasks = std::vector<AdaptationTask>();

	utilities = new Utilities();

	utilities->resetRandoms();
	//generate all of the students models
	students = std::vector<Student*>();
	for (int i = 0; i < numStudentsInClass; i++) {
		students.push_back(new Student(i, "a", numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell, numIterations, utilities));
	}

	

	statisticsFile = std::ofstream("./statistics.txt", std::ios::in | std::ios::out);
	resultsFile = std::ofstream("./results.txt", std::ios::in | std::ios::out);

}
void Core::reset() {
	//generate all of the students models
	for (int i = 0; i < numStudentsInClass; i++) {
		Student* currStudent = students[i];
		currStudent->reset(numStudentModelCells, maxAmountOfStoredProfilesPerCell);
	}
}
Core::~Core(){
	for (int i = 0; i < numStudentsInClass; i++) {
		delete students[i];
	}
}

void Core::simulateStudentsReaction(int currIteration) {
	//simulate students reaction
	for (int j = 0; j < numStudentsInClass; j++) {
		Student* currStudent = students[j];
		currStudent->simulateReaction(currIteration);
	}
}


void Core::simulateTrainingPhase() {
	Adaptation randomClose = Adaptation(numStudentsInClass, 10, minNumStudentsPerGroup, maxNumStudentsPerGroup, 5, 0, numTrainingCycles, numTasksPerGroup, utilities);
	simulateAdaptationModule(0, &randomClose, 0);
}

void Core::storeSimData(std::string configId, Adaptation* adapt) {
	std::vector<int> groupSizeFreqs = adapt->groupSizeFreqs;
	std::vector<int> configSizeFreqs = adapt->configSizeFreqs;

	std::vector<double> avgAbilities = adapt->avgAbilities;
	std::vector<double> avgEngagements = adapt->avgEngagements;
	std::vector<double> avgPrefDiff = adapt->avgPrefDiff;
	double avgExecutionTime = adapt->avgExecutionTime;

	int numAdaptationCycles = adapt->getNumAdaptationCycles();
	int numStudentsInClass = adapt->getNumStudentsInClass();

	statisticsFile << "timesteps=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		statisticsFile << i;
		if (i != (numAdaptationCycles - 1)) {
			statisticsFile << ",";
		}
	}
	statisticsFile << "]\n";

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
	//return statisticsFile;
}

void Core::executeSimulation(int numRuns, Adaptation* adapt) {

	int numAdaptationCycles = adapt->getNumAdaptationCycles();

	for (int i = 0; i < numRuns; i++) {
		reset();
		simulateTrainingPhase();
		simulateAdaptationModule(i, adapt, numTrainingCycles);
		//destroyGlobals(numStudentsInClass);
	}

	storeSimData("GAL100", adapt);
	statisticsFile.close();
}


void Core::executeAdaptationStep(int currStepIndex, int currRun, Adaptation* adapt) {

	AdaptationConfiguration currAdaptedConfig = adapt->getCurrAdaptedConfig();
	std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;
	
	//extract adapted mechanics
	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> groupMechanicPairs;

	groupMechanicPairs = adapt->iterate(students, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks, currStepIndex);

	int mechanicsSize = groupMechanicPairs.size();

	/*statisticsFile << "currProfile: " << students[0]->getCurrProfile().K_cl << students[0]->getCurrProfile().K_cp << students[0]->getCurrProfile().K_i << std::endl;
	statisticsFile << "ability: " << students[0]->getAbility() << std::endl;
	statisticsFile << "preference: " << students[0]->getEngagement() << std::endl;*/

	//intervene
	for (int j = 0; j < mechanicsSize; j++) {
		std::vector<Student*> currGroup = groupMechanicPairs[j].first.getStudents();
		std::vector<AdaptationTask> currMechanic = groupMechanicPairs[j].second;

		resultsFile << "promote on students:" << std::endl;
		for (int k = 0; k < currGroup.size(); k++) {
			resultsFile << "Number: " << currGroup[k]->getId() << ", Name: " << currGroup[k]->getName() << std::endl;
		}
		resultsFile << ", the following tasks:" << std::endl;
		for (int k = 0; k < currMechanic.size(); k++) {
			resultsFile << currMechanic[k].description << std::endl;
		}
		resultsFile << "-- -- -- -- -- -- -- -- -- -- -- -- --" << std::endl;
	}
	resultsFile << "----------------------End of Iteration--------------------" << std::endl;
}

void Core::simulateAdaptationModule(int currRun, Adaptation* adapt, int initialStep) {
	int i = 0;
	int numAdaptationCycles = adapt->getNumAdaptationCycles();
	while (true) {
		const clock_t beginTime = clock();
		printf("\rstep %d of %d of run %d", i, numAdaptationCycles, currRun);

		AdaptationConfiguration currAdaptedConfig = adapt->getCurrAdaptedConfig();
		std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;

		for (int j = 0; j < groups.size(); j++) {
			adapt->avgPrefDiff[i] += groups[j].getAvgPreferences().distanceBetween(groups[j].getInteractionsProfile()) / (groups.size() * numRuns);
		}
		for (int j = 0; j < numStudentsInClass; j++) {
			adapt->avgAbilities[i] += students[j]->currModelIncreases.ability / (numStudentsInClass * numRuns);
			adapt->avgEngagements[i] += students[j]->currModelIncreases.engagement / (numStudentsInClass * numRuns);
		}

		executeAdaptationStep(initialStep + i, currRun, adapt);
		if (i > (adapt->getNumAdaptationCycles() - 1)) {
			break;
		}
		
		simulateStudentsReaction(initialStep + i);
		adapt->avgExecutionTime += (float(clock() - beginTime) / CLOCKS_PER_SEC) / (numAdaptationCycles*numRuns);
		i++;
	}
}
