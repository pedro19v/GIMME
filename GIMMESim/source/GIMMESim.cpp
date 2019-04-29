#include "../headers/GIMMESim.h"


GIMMESim::GIMMESim(
	int numRuns, int numIterationsPerRun, int numTrainingCycles,
	int numStudentsInClass, int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell,
	int numConfigurtionChoices, int numFitnessNNs, int timeWindow,
	int minNumStudentsPerGroup, int maxNumStudentsPerGroup,
	int numTasksPerGroup,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks) {

	this->students = students;

	this->numRuns = numRuns;
	this->numTrainingCycles = numTrainingCycles;
	this->numConfigurationChoices = numConfigurtionChoices;
	this->numFitnessNNs = numFitnessNNs;
	this->timeWindow = timeWindow;
	this->minNumStudentsPerGroup = minNumStudentsPerGroup;
	this->maxNumStudentsPerGroup = maxNumStudentsPerGroup;

	this->numTasksPerGroup = numTasksPerGroup;
	this->numStudentsInClass = numStudentsInClass;
	this->numStudentModelCells = numberOfStudentModelCells;
	this->maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;

	this->numIterationsPerRun = numIterationsPerRun;

	//define and init globals and utilities
	utilities = new Utilities();
	utilities->resetRandoms();

	//generate all of the students models
	students = std::vector<Student*>();
	for (int i = 0; i < numStudentsInClass; i++) {
		students.push_back(new SimStudent(i, "a", numStudentModelCells, maxAmountOfStoredProfilesPerCell, numIterationsPerRun + 30, utilities));
	}


	possibleCollaborativeTasks = std::vector<AdaptationTask>();
	possibleCompetitiveTasks = std::vector<AdaptationTask>();
	possibleIndividualTasks = std::vector<AdaptationTask>();

	this->adapt = new Adaptation(
		"GIMME",
		&students,
		numConfigurationChoices,
		minNumStudentsPerGroup, maxNumStudentsPerGroup,
		numFitnessNNs, 2,
		numIterationsPerRun,
		utilities, numTasksPerGroup,
		possibleCollaborativeTasks,
		possibleCompetitiveTasks,
		possibleIndividualTasks
	);

	
	possibleCollaborativeTasks = std::vector<AdaptationTask>();
	possibleCompetitiveTasks = std::vector<AdaptationTask>();
	possibleIndividualTasks = std::vector<AdaptationTask>();
	
	statisticsFile = new std::fstream();
	resultsFile = new std::fstream();

	statisticsFile->open("./statistics.txt", std::fstream::out);
	resultsFile->open("./results.txt", std::fstream::out);

}

void GIMMESim::reset() {
	//generate all of the students models
	for (int i = 0; i < numStudentsInClass; i++) {
		SimStudent* currStudent = (SimStudent*) students[i];
		currStudent->reset(numStudentModelCells, maxAmountOfStoredProfilesPerCell);
	}
}
GIMMESim::~GIMMESim() {
	/*for (int i = 0; i < numStudentsInClass; i++) {
		delete students[i];
	}*/

	delete adapt;
	
	delete statisticsFile;
	delete resultsFile;
}

void GIMMESim::simulateStudentsReaction(int currIteration) {
	//simulate students reaction
	for (int j = 0; j < numStudentsInClass; j++) {
		SimStudent* currStudent = (SimStudent*) students[j];
		currStudent->simulateReaction(currIteration);
	}
}


void GIMMESim::simulateTrainingPhase() {
	Adaptation randomClose = Adaptation(
		"randomClose",
		&students,
		numConfigurationChoices,
		minNumStudentsPerGroup, maxNumStudentsPerGroup,
		numFitnessNNs, 0,
		30,
		utilities, numTasksPerGroup,
		possibleCollaborativeTasks,
		possibleCompetitiveTasks,
		possibleIndividualTasks
	);

	simulateAdaptationModule(0, &randomClose, 0);
}

void GIMMESim::storeSimData(std::string configId, Adaptation* adapt) {
	std::vector<int> groupSizeFreqs = adapt->groupSizeFreqs;
	std::vector<int> configSizeFreqs = adapt->configSizeFreqs;

	std::vector<double> avgAbilities = adapt->avgAbilities;
	std::vector<double> avgEngagements = adapt->avgEngagements;
	std::vector<double> avgPrefDiff = adapt->avgPrefDiff;
	double avgExecutionTime = adapt->avgExecutionTime;

	int numAdaptationCycles = adapt->getNumAdaptationCycles();
	//int numStudentsInClass = adapt->getNumStudentsInClass();

	*statisticsFile << "timesteps=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		*statisticsFile << i;
		if (i != (numAdaptationCycles - 1)) {
			*statisticsFile << ",";
		}
	}
	*statisticsFile << "]\n";

	*statisticsFile << configId.c_str() << "Abilities=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		*statisticsFile << avgAbilities[i];
		if (i != (numAdaptationCycles - 1)) {
			*statisticsFile << ",";
		}
	}
	*statisticsFile << "]\n";

	*statisticsFile << configId.c_str() << "Engagements=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		*statisticsFile << avgEngagements[i];
		if (i != (numAdaptationCycles - 1)) {
			*statisticsFile << ",";
		}
	}
	*statisticsFile << "]\n\n";


	*statisticsFile << configId.c_str() << "PrefDiffs=[";
	for (int i = 0; i < numAdaptationCycles; i++) {
		*statisticsFile << avgPrefDiff[i];
		if (i != (numAdaptationCycles - 1)) {
			*statisticsFile << ",";
		}
	}
	*statisticsFile << "]\n";


	*statisticsFile << configId.c_str() << "groupSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass; i++) {
		*statisticsFile << groupSizeFreqs[i];
		if (i != (numStudentsInClass - 1)) {
			*statisticsFile << ",";
		}
	}
	*statisticsFile << "]\n";


	*statisticsFile << configId.c_str() << "configSizeFreqs=[";
	for (int i = 0; i < numStudentsInClass; i++) {
		*statisticsFile << configSizeFreqs[i];
		if (i != (numStudentsInClass - 1)) {
			*statisticsFile << ",";
		}
	}
	*statisticsFile << "]\n";


	*statisticsFile << configId.c_str() << "avgExecTime=" << avgExecutionTime;
	*statisticsFile << "\n\n";

	//return statisticsFile;
	statisticsFile->flush();
	statisticsFile->close();
}


void GIMMESim::executeAdaptationStep(int currStepIndex, int currRun) {

	AdaptationConfiguration currAdaptedConfig = adapt->getCurrAdaptedConfig();
	std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;

	//extract adapted mechanics
	std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> groupMechanicPairs;

	groupMechanicPairs = adapt->iterate(currStepIndex);

	int mechanicsSize = (int) groupMechanicPairs.size();

	/**statisticsFile << "currProfile: " << students[0]->getCurrProfile().K_cl << students[0]->getCurrProfile().K_cp << students[0]->getCurrProfile().K_i << std::endl;
	*statisticsFile << "ability: " << students[0]->getCurrState().characteristics.ability << std::endl;
	*statisticsFile << "preference: " << students[0]->getCurrState().characteristics.engagement << std::endl;*/

	//intervene
	for (int j = 0; j < mechanicsSize; j++) {
		std::vector<Student*> currGroup = groupMechanicPairs[j].first.getStudents();
		std::vector<AdaptationTask> currMechanic = groupMechanicPairs[j].second.tasks;


		*resultsFile << "promote on students:" << std::endl;
		for (int k = 0; k < currGroup.size(); k++) {
			*resultsFile << "Number: " << currGroup[k]->getId() << ", Name: " << currGroup[k]->getName() << std::endl;
		}
		*resultsFile << ", the following tasks:" << std::endl;
		for (int k = 0; k < currMechanic.size(); k++) {
			*resultsFile << currMechanic[k].description << std::endl;
		}
		*resultsFile << "-- -- -- -- -- -- -- -- -- -- -- -- --" << std::endl;
	}
	*resultsFile << "----------------------End of Iteration--------------------" << std::endl;
	resultsFile->flush();
}

void GIMMESim::simulate() {
	for (int i = 0; i < numRuns; i++) {
		reset();
		simulateTrainingPhase();
		simulateAdaptationModule(i, adapt, numTrainingCycles);
		//destroyGlobals(numStudentsInClass);
	}

	storeSimData(adapt->getName(), adapt);
}
void GIMMESim::simulateAdaptationModule(int currRun, Adaptation* adapt, int initialStep) {
	int i = 0;
	int numAdaptationCycles = adapt->getNumAdaptationCycles();
	while (true) {
		const clock_t beginTime = clock();
		printf("\rstep %d of %d of run %d               ", i, numAdaptationCycles, currRun);

		AdaptationConfiguration currAdaptedConfig = adapt->getCurrAdaptedConfig();
		std::vector<AdaptationGroup> groups = currAdaptedConfig.groups;

		for (int j = 0; j < groups.size(); j++) {
			adapt->avgPrefDiff[i] += groups[j].getAvgPreferences().distanceBetween(groups[j].getInteractionsProfile()) / (groups.size() * numRuns);
		}
		for (int j = 0; j < numStudentsInClass; j++) {
			adapt->avgAbilities[i] += students[j]->currModelIncreases.characteristics.ability / (numStudentsInClass * numRuns);
			adapt->avgEngagements[i] += students[j]->currModelIncreases.characteristics.engagement / (numStudentsInClass * numRuns);
		}

		executeAdaptationStep(initialStep + i, currRun);
		if (i > (adapt->getNumAdaptationCycles() - 1)) {
			break;
		}

		simulateStudentsReaction(initialStep + i);
		adapt->avgExecutionTime += (float(clock() - beginTime) / CLOCKS_PER_SEC) / (numAdaptationCycles*numRuns);
		i++;
	}
}

