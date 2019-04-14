#include "../headers/Adaptation.h"

Adaptation::Adaptation(
	std::vector<Student*> students,
	int numberOfConfigChoices,
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup,
	int numberOfFitnessNNs, int fitnessCondition,
	int numAdaptationCycles,
	Utilities* utilities, int numTasksPerGroup,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks){

	this->students = students;
	int studentSize = (int) students.size();


	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;
	this->minNumberOfStudentsPerGroup = minNumberOfStudentsPerGroup;

	this->numTasksPerGroup = numTasksPerGroup;
	this->numberOfFitnessNNs = numberOfFitnessNNs;
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
	std::vector<Student*> students,
	int numberOfConfigChoices,
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup,
	int numberOfFitnessNNs,
	Utilities* utilities, int numTasksPerGroup,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks): 
	Adaptation(students,
		numberOfConfigChoices,
		minNumberOfStudentsPerGroup, maxNumberOfStudentsPerGroup,
		numberOfFitnessNNs, 2,
		0,
		utilities, numTasksPerGroup,
		possibleCollaborativeTasks,
		possibleCompetitiveTasks,
		possibleIndividualTasks)
{ }




std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> Adaptation::iterate(int currIteration)
{
	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> groupMechanicPairs = std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>>();

	adaptedConfig = organizeStudents(students, currIteration);
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
		LearningState currGroupState = currGroup.getAvgLearningState();
		groupMechanicPairs.push_back({ currGroup , generateMechanic(currGroupProfile, currGroupState, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks) });
	}
	
	return groupMechanicPairs;
}
std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> Adaptation::iterate()
{
	return iterate(0);
}

AdaptationConfiguration Adaptation::getCurrAdaptedConfig() {
	return this->adaptedConfig;
}


int Adaptation::getNumAdaptationCycles() {
	return this->numAdaptationCycles;
}


AdaptationConfiguration Adaptation::organizeStudents(std::vector<Student*> students, int currIteration) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = -INFINITY;


	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		bool lastProfile = false;
		double currFitness = 0.0;
		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(students);
		int studentsSize = (int) students.size();
		AdaptationConfiguration newConfig = AdaptationConfiguration();
		
		int minNumGroups = (int) ceil((double) students.size() / (double) maxNumberOfStudentsPerGroup);
		int maxNumGroups = (int) floor((double) students.size() / (double) minNumberOfStudentsPerGroup);
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

				double currStudentFitness = fitness(currStudent, currGroup.getInteractionsProfile(), this->numberOfFitnessNNs, currIteration);
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

			double currStudentFitness = fitness(currStudent, currGroup->getInteractionsProfile(), this->numberOfFitnessNNs, currIteration);
			currFitness += currStudentFitness;

			studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			studentsWithoutGroupSize = (int) studentsWithoutGroup.size();
		}

		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
		int currGroupsSize = (int)currGroups->size();
		this->configSizeFreqs[currGroupsSize]++;
		for (int s = 0; s < currGroupsSize; s++) {
			AdaptationGroup currGroup = (*currGroups)[s];
			this->groupSizeFreqs[(int) currGroup.getStudents().size()]++;
		}

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


double Adaptation::fitness(Student* student, InteractionsProfile profile, int numberOfFitnessNNs, int currIteration) {

	if (fitnessCondition == 1) {
		double engagement = 0;
		double predSimAbility = student->getCurrState().ability;
		student->calcReaction(&engagement, &predSimAbility, &profile, currIteration);
		double abilityInc = predSimAbility - student->getCurrState().ability;
		return abilityInc;
	}

	std::vector<LearningState> pastModelIncs = student->getPastModelIncreases();
	std::vector<LearningState> pastModelncsCopy = std::vector<LearningState>(pastModelIncs);
	int pastModelIncsSize = (int) pastModelIncs.size();

	LearningState predictedModel = { profile, 0 , 0 };
	std::sort(pastModelncsCopy.begin(), pastModelncsCopy.end(), FitnessSort(this, profile));

	if (pastModelIncsSize > numberOfFitnessNNs) {
		pastModelncsCopy.resize(numberOfFitnessNNs);
	}
	int pastModelncsCopySize = (int) pastModelncsCopy.size();

	predictedModel.ability = 0;
	predictedModel.engagement = 0;
	for (int i = 0; i < pastModelncsCopySize; i++) {
		InteractionsProfile pastProfile = pastModelncsCopy[i].profile;
		double distance = profile.distanceBetween(pastProfile);

		predictedModel.ability += pastModelncsCopy[i].ability* (1 - distance) / (double) (pastModelncsCopySize); //* (1 - distance) 
		predictedModel.engagement += pastModelncsCopy[i].engagement* (1 - distance) / (double)(pastModelncsCopySize); //* (1 - distance)
	}

	return 0.5*(predictedModel.ability) + 0.5*predictedModel.engagement; //ability must be normalized to [0,1]
}

std::vector<AdaptationTask> Adaptation::generateMechanic(InteractionsProfile bestConfigProfile,
	LearningState avgLearningState,
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
	return mechanicTasks;
}

AdaptationTask Adaptation::pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, LearningState avgLearningState)
{
	int randIndex = utilities->randIntBetween(0, (int) possibleTasks.size() - 1);
	AdaptationTask randomTask = possibleTasks[randIndex];
	std::vector<AdaptationTask> randomTaskInstances = randomTask.taskInstances;
	int randomTaskInstancesSize = (int) randomTaskInstances.size();
	//pick the right difficulty
	AdaptationTask adaptedInstance = randomTaskInstances[0];
	for (int j = 1; j < randomTaskInstancesSize; j++) {
		AdaptationTask currInstance = randomTaskInstances[j];
		float minRequiredAbility = currInstance.minRequiredAbility;
		if (minRequiredAbility < avgLearningState.ability && minRequiredAbility > adaptedInstance.minRequiredAbility) {
			adaptedInstance = currInstance;
		}
	}
	return adaptedInstance;
}
