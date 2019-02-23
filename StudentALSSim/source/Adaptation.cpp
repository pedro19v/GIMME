#include "../headers/Adaptation.h"

Adaptation::Adaptation(int studentSize, int numberOfConfigChoices, 
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, 
	int numberOfFitnessNNs, int fitnessCondition, int numAdaptationCycles,
	int numTasksPerGroup) {

	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;
	this->minNumberOfStudentsPerGroup = minNumberOfStudentsPerGroup;

	this->numTasksPerGroup = numTasksPerGroup;

	this->numberOfFitnessNNs = numberOfFitnessNNs;

	this->fitnessCondition = fitnessCondition;

	this->avgAbilities = std::vector<double>(numAdaptationCycles+1);
	this->avgEngagements = std::vector<double>(numAdaptationCycles+1);
	this->avgPrefDiff = std::vector<double>(numAdaptationCycles+1);
	this->avgExecutionTime = 0;

	this->groupSizeFreqs = std::vector<int>(studentSize+1);
	this->configSizeFreqs = std::vector<int>(studentSize+1);

	this->numAdaptationCycles = numAdaptationCycles;
}

std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> Adaptation::iterate(std::vector<Student*> students, 
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks,
	int currIteration)
{
	std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>> groupMechanicPairs = std::vector<std::pair<AdaptationGroup, std::vector<AdaptationTask>>>();

	adaptedConfig = organizeStudents(students, currIteration);
	std::vector<AdaptationGroup> groups = adaptedConfig.groups;
	int groupsSize = groups.size();
	for (int i = 0; i < groupsSize; i++) {
		AdaptationGroup currGroup = groups[i];
		std::vector<Student*> groupStudents = currGroup.getStudents();
		int groupStudentsSize = groupStudents.size();

		for (int j = 0; j < groupStudentsSize; j++) {
			Student* currStudent = groupStudents[j];
			currStudent->changeCurrProfile(currGroup.getLearningProfile());
		}

		Utilities::LearningProfile currGroupProfile = currGroup.getLearningProfile();
		Student::LearningState currGroupState = currGroup.getAvgLearningState();
		groupMechanicPairs.push_back({ currGroup , generateMechanic(currGroupProfile, currGroupState, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks) });
	}
	
	return groupMechanicPairs;
}

AdaptationConfiguration Adaptation::getCurrAdaptedConfig() {
	return this->adaptedConfig;
}


int Adaptation::getNumAdaptationCycles() {
	return this->numAdaptationCycles;
}


AdaptationConfiguration Adaptation::organizeStudents(std::vector<Student*> students, int currIteration) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = 0.0;


	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		bool lastProfile = false;
		double currFitness = 0.0;
		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(students);
		int studentsSize = students.size();
		AdaptationConfiguration newConfig = AdaptationConfiguration();
		
		int minNumGroups = std::ceil((double) Globals::students.size() / (double) maxNumberOfStudentsPerGroup);
		int maxNumGroups = std::floor((double) Globals::students.size() / (double) minNumberOfStudentsPerGroup);
		int numGroups = Utilities::randIntBetween(minNumGroups,maxNumGroups);
		
		//generate min groups
		int studentsWithoutGroupSize = 0;
		for (int k = 0; k < numGroups; k++) {

			AdaptationGroup currGroup = AdaptationGroup();

			//generate learning profile
			double newRand1 = Utilities::randBetween(0, 1);
			double newRand2 = Utilities::randBetween(0, 1);
			double newRand3 = Utilities::randBetween(0, 1);

			double newRandSum = newRand1 + newRand2 + newRand3;

			Utilities::LearningProfile profile = Utilities::LearningProfile();
			profile.K_cl = newRand1/ newRandSum;
			profile.K_cp = newRand2/ newRandSum;
			profile.K_i = newRand3/ newRandSum;
			currGroup.setLearningProfile(profile);


			for (int s = 0; s < minNumberOfStudentsPerGroup; s++) {
				studentsWithoutGroupSize = studentsWithoutGroup.size();
				int currStudentIndex = Utilities::randIntBetween(0,studentsWithoutGroupSize-1);

				Student* currStudent = studentsWithoutGroup[currStudentIndex];
				currGroup.addStudent(currStudent);

				double currStudentFitness = fitness(currStudent, currGroup.getLearningProfile(), this->numberOfFitnessNNs, currIteration);
				currFitness += currStudentFitness;

				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			}

			newConfig.groups.push_back(currGroup);
		}

		studentsWithoutGroupSize = studentsWithoutGroup.size();
		while (studentsWithoutGroupSize > 0) {
			int randomGroupIndex = Utilities::randIntBetween(0, newConfig.groups.size() - 1);

			int currStudentIndex = 0;
			if (studentsWithoutGroupSize > 1) {
				currStudentIndex = Utilities::randIntBetween(0, studentsWithoutGroupSize - 1);
			}

			AdaptationGroup* currGroup = &newConfig.groups[randomGroupIndex];
			int groupsSize = newConfig.groups.size();
			while (currGroup->getStudents().size() > maxNumberOfStudentsPerGroup - 1) {
				currGroup = &newConfig.groups[randomGroupIndex++%groupsSize];
			}

			Student* currStudent = studentsWithoutGroup[currStudentIndex];
			currGroup->addStudent(currStudent);

			double currStudentFitness = fitness(currStudent, currGroup->getLearningProfile(), this->numberOfFitnessNNs, currIteration);
			currFitness += currStudentFitness;

			studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			studentsWithoutGroupSize = studentsWithoutGroup.size();
		}

		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
		this->configSizeFreqs[currGroups->size()]++;
		for (int s = 0; s < currGroups->size(); s++) {
			AdaptationGroup currGroup = (*currGroups)[s];
			this->groupSizeFreqs[currGroup.getStudents().size()]++;
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


double Adaptation::fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs, int currIteration) {

	if (fitnessCondition == 1) {
		double engagement = 0;
		double predSimAbility = student->getAbility();

		student->calcReaction(&engagement, &predSimAbility, &profile, currIteration);

		double abilityInc = predSimAbility - student->getAbility();

		return abilityInc;
	}

	std::vector<Student::LearningState> pastModelIncs = student->getPastModelIncreases();
	std::vector<Student::LearningState> pastModelncsCopy = std::vector<Student::LearningState>(pastModelIncs);
	int pastModelIncsSize = pastModelIncs.size();

	Student::LearningState predictedModel = { profile, 0 , 0 };
	std::sort(pastModelncsCopy.begin(), pastModelncsCopy.end(), FitnessSort(this, profile));

	pastModelncsCopy.resize(numberOfFitnessNNs);
	int pastModelncsCopySize = pastModelncsCopy.size();

	predictedModel.ability = 0;
	predictedModel.engagement = 0;
	for (int i = 0; i < pastModelncsCopySize; i++) {
		Utilities::LearningProfile pastProfile = pastModelncsCopy[i].currProfile;
		double distance = profile.distanceBetween(pastProfile);

		predictedModel.ability += pastModelncsCopy[i].ability* (1 - distance) / (double) (pastModelncsCopySize); //* (1 - distance) 
		predictedModel.engagement += pastModelncsCopy[i].engagement* (1 - distance) / (double)(pastModelncsCopySize); //* (1 - distance)
	}

	return 0.5*(predictedModel.ability) + 0.5*predictedModel.engagement; //ability must be normalized to [0,1]
}

std::vector<AdaptationTask> Adaptation::generateMechanic(Utilities::LearningProfile bestConfigProfile,
	Student::LearningState avgLearningState,
	std::vector<AdaptationTask> possibleCollaborativeTasks,
	std::vector<AdaptationTask> possibleCompetitiveTasks,
	std::vector<AdaptationTask> possibleIndividualTasks) {

	
	int collaborativeTaskSize = std::ceil(bestConfigProfile.K_cl*numTasksPerGroup);
	int competitiveTaskSize = std::ceil(bestConfigProfile.K_cp*numTasksPerGroup);
	int individualTaskSize = std::ceil(bestConfigProfile.K_i*numTasksPerGroup);

	std::vector<AdaptationTask> mechanicTasks = std::vector<AdaptationTask>();
	
	for (int i = 0; i < collaborativeTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(Globals::possibleCollaborativeTasks, avgLearningState));
	}
	for (int i = 0; i < competitiveTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(Globals::possibleCompetitiveTasks, avgLearningState));
	}
	for (int i = 0; i < individualTaskSize; i++) {
		mechanicTasks.push_back(pickRandTaskInstance(Globals::possibleIndividualTasks, avgLearningState));
	}
	Utilities::randShuffle(mechanicTasks);
	return mechanicTasks;
}

AdaptationTask Adaptation::pickRandTaskInstance(std::vector<AdaptationTask> possibleTasks, Student::LearningState avgLearningState)
{
	int randIndex = Utilities::randIntBetween(0, possibleTasks.size() - 1);
	AdaptationTask randomTask = possibleTasks[randIndex];
	std::vector<AdaptationTask> randomTaskInstances = randomTask.taskInstances;
	int randomTaskInstancesSize = randomTaskInstances.size();
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
