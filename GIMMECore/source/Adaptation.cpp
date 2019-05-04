#include "../headers/Adaptation.h"

Adaptation::Adaptation()
{
}

Adaptation::Adaptation(
	std::string name,
	std::vector<Student*>* students,
	int numberOfConfigChoices,
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup,
	IRegressionAlg regAlg, int fitnessCondition,
	int numAdaptationCycles,
	Utilities* utilities, int numTasksPerGroup,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks){


	this->name = name;

	this->students = students;
	int studentSize = (int) students->size();


	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;
	this->minNumberOfStudentsPerGroup = minNumberOfStudentsPerGroup;

	this->numTasksPerGroup = numTasksPerGroup;
	this->regAlg = regAlg;
	this->fitnessCondition = fitnessCondition;

	this->numAdaptationCycles = numAdaptationCycles;
	this->avgAbilities = std::vector<double>(numAdaptationCycles+1);
	this->avgEngagements = std::vector<double>(numAdaptationCycles+1);
	this->avgPrefDiff = std::vector<double>(numAdaptationCycles+1);
	this->avgExecutionTime = 0;

	this->groupSizeFreqs = std::vector<int>(studentSize+1);
	this->configSizeFreqs = std::vector<int>(studentSize+1);

	this->utilities = utilities;

	this->possibleCollaborativeTasks = possibleCollaborativeTasks;
	this->possibleCompetitiveTasks = possibleCompetitiveTasks;
	this->possibleIndividualTasks = possibleIndividualTasks;
}

Adaptation::Adaptation(
	std::string name,
	std::vector<Student*>* students,
	int numberOfConfigChoices,
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup,
	IRegressionAlg regAlg,
	Utilities* utilities, 
	int numTasksPerGroup,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks):
	Adaptation(
		name,
		students,
		numberOfConfigChoices,
		minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup,
		regAlg, 0,
		2,
		utilities, numTasksPerGroup,
		possibleCollaborativeTasks,
		possibleCompetitiveTasks,
		possibleIndividualTasks
	) {
}

std::string Adaptation::getName()
{
	return this->name;
}




std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> Adaptation::iterate(int currIteration)
{
	std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> groupMechanicPairs = std::vector<std::pair<AdaptationGroup, AdaptationMechanic>>();

	adaptedConfig = organizeStudents(currIteration);
	std::vector<AdaptationGroup> groups = adaptedConfig.groups;
	int groupsSize = (int) groups.size();
	for (int i = 0; i < groupsSize; i++) {
		AdaptationGroup currGroup = groups[i];
		std::vector<Student*> groupStudents = currGroup.getStudents();
		int groupStudentsSize = (int) groupStudents.size();

		for (int j = 0; j < groupStudentsSize; j++) {
			Student* currStudent = groupStudents[j];
			currStudent->setCurrProfile(currGroup.getInteractionsProfile());
		}

		InteractionsProfile currGroupProfile = currGroup.getInteractionsProfile();
		PlayerState currGroupState = currGroup.getAvgLearningState();
		groupMechanicPairs.push_back({ currGroup , generateMechanic(currGroupProfile, currGroupState, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks) });
	}
	
	return groupMechanicPairs;
}
std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> Adaptation::iterate()
{
	return iterate(0);
}

AdaptationConfiguration Adaptation::getCurrAdaptedConfig() {
	return this->adaptedConfig;
}


int Adaptation::getNumAdaptationCycles() {
	return this->numAdaptationCycles;
}


AdaptationConfiguration Adaptation::organizeStudents(int currIteration) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = -INFINITY;


	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		bool lastProfile = false;
		double currFitness = 0.0;
		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(*students);
		int studentsSize = (int) students->size();
		AdaptationConfiguration newConfig = AdaptationConfiguration();
		
		int minNumGroups = (int) ceil((double) students->size() / (double) maxNumberOfStudentsPerGroup);
		int maxNumGroups = (int) floor((double) students->size() / (double) minNumberOfStudentsPerGroup);
		int numGroups = utilities->randIntBetween(minNumGroups,maxNumGroups);
		
		//generate min groups
		int studentsWithoutGroupSize = 0;
		for (int k = 0; k < numGroups; k++) {

			AdaptationGroup currGroup = AdaptationGroup();

			//generate learning profile
			double newRand1 = utilities->randBetween(0, 1);
			double newRand2 = utilities->randBetween(0, 1);
			double newRand3 = utilities->randBetween(0, 1);

			double newRandSum = newRand1 + newRand2 + newRand3;

			InteractionsProfile profile = InteractionsProfile();
			profile.K_cl = newRand1/ newRandSum;
			profile.K_cp = newRand2/ newRandSum;
			profile.K_i = newRand3/ newRandSum;
			currGroup.setInteractionsProfile(profile);


			for (int s = 0; s < minNumberOfStudentsPerGroup; s++) {
				studentsWithoutGroupSize = (int) studentsWithoutGroup.size();
				int currStudentIndex = utilities->randIntBetween(0,studentsWithoutGroupSize-1);

				Student* currStudent = studentsWithoutGroup[currStudentIndex];
				currGroup.addStudent(currStudent);

				double currStudentFitness = fitness(currStudent, currGroup.getInteractionsProfile(), currIteration);
				currFitness += currStudentFitness;

				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			}

			newConfig.groups.push_back(currGroup);
		}

		studentsWithoutGroupSize = (int) studentsWithoutGroup.size();
		while (studentsWithoutGroupSize > 0) {
			int randomGroupIndex = utilities->randIntBetween(0, (int) newConfig.groups.size() - 1);

			int currStudentIndex = 0;
			if (studentsWithoutGroupSize > 1) {
				currStudentIndex = utilities->randIntBetween(0, studentsWithoutGroupSize - 1);
			}

			AdaptationGroup* currGroup = &newConfig.groups[randomGroupIndex];
			int groupsSize = (int) newConfig.groups.size();
			while ((int) currGroup->getStudents().size() > maxNumberOfStudentsPerGroup - 1) {
				currGroup = &newConfig.groups[randomGroupIndex++%groupsSize];
			}

			Student* currStudent = studentsWithoutGroup[currStudentIndex];
			currGroup->addStudent(currStudent);

			double currStudentFitness = fitness(currStudent, currGroup->getInteractionsProfile(), currIteration);
			currFitness += currStudentFitness;

			studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			studentsWithoutGroupSize = (int) studentsWithoutGroup.size();
		}

		int studentSize = students->size();
		this->groupSizeFreqs.resize(studentSize + 1);
		this->configSizeFreqs.resize(studentSize + 1);
		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
		int currGroupsSize = (int)currGroups->size();
		this->configSizeFreqs[currGroupsSize]++;
		for (int s = 0; s < currGroupsSize; s++) {
			AdaptationGroup currGroup = (*currGroups)[s];
			this->groupSizeFreqs[(int) currGroup.getStudents().size()]++;
		}

		//return random config when fitnessCondition = 0
		if (fitnessCondition == 0) {
			return newConfig;
		}

		if (currFitness > currMaxFitness) {
			bestConfig = newConfig;
			currMaxFitness = currFitness;
		}
	}
	return bestConfig;
}


double Adaptation::fitness(Student* student, InteractionsProfile profile, int currIteration) {

	//this is the optimal simulation condition, therefore the 'wierd' cast...
	if (fitnessCondition == 1) { 
		/*double engagement = student->getCurrState().characteristics.engagement;
		double ability = student->getCurrState().characteristics.ability;*/
		PlayerState predictedState = PlayerState(student->getCurrState());

		//((SimStudent*)student)->calcReaction(&predictedState, currIteration);
		double abilityInc = predictedState.characteristics.ability - student->getCurrState().characteristics.ability;
		return abilityInc;
	}

	FitnessSort sort = FitnessSort(this, profile);
	PlayerState predictedModel = regAlg.predict(profile, student, &sort);
	return 0.5*(predictedModel.characteristics.ability) + 0.5*predictedModel.characteristics.engagement; //ability must be normalized to [0,1]
}

AdaptationMechanic Adaptation::generateMechanic(InteractionsProfile bestConfigProfile,
	PlayerState avgLearningState,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks) {

	
	int collaborativeTaskSize = (int) ceil(bestConfigProfile.K_cl*numTasksPerGroup);
	int competitiveTaskSize = (int) ceil(bestConfigProfile.K_cp*numTasksPerGroup);
	int individualTaskSize = (int) ceil(bestConfigProfile.K_i*numTasksPerGroup);

	std::vector<AdaptationTask> mechanicTasks = std::vector<AdaptationTask>();
	
	for (int i = 0; i < collaborativeTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(possibleCollaborativeTasks, avgLearningState));
	}
	for (int i = 0; i < competitiveTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(possibleCompetitiveTasks, avgLearningState));
	}
	for (int i = 0; i < individualTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(possibleIndividualTasks, avgLearningState));
	}
	utilities->randShuffle(mechanicTasks);

	AdaptationMechanic mechanic = { bestConfigProfile, mechanicTasks };
	return mechanic;
}

AdaptationTask Adaptation::pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, PlayerState avgLearningState)
{
	if (possibleTasks.empty()) {
		return AdaptationTask(AdaptationTaskType::NONE, "default", 0.0f);
	}
	int randIndex = utilities->randIntBetween(0, (int) possibleTasks.size() - 1);
	AdaptationTask randomTask = possibleTasks[randIndex];
	std::vector<AdaptationTask> randomTaskInstances = randomTask.taskInstances;
	int randomTaskInstancesSize = (int) randomTaskInstances.size();
	
	//pick the right difficulty
	AdaptationTask adaptedInstance = randomTaskInstances[0];
	for (int j = 1; j < randomTaskInstancesSize; j++) {
		AdaptationTask currInstance = randomTaskInstances[j];
		float minRequiredAbility = currInstance.minRequiredAbility;
		if (minRequiredAbility < avgLearningState.characteristics.ability && minRequiredAbility > adaptedInstance.minRequiredAbility) {
			adaptedInstance = currInstance;
		}
	}
	return adaptedInstance;
}
