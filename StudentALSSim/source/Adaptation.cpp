#include "../headers/Adaptation.h"

Adaptation::Adaptation(int numberOfConfigChoices, 
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, 
	int numberOfFitnessNNs, int fitnessCondition, int numAdaptationCycles) {

	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;
	this->minNumberOfStudentsPerGroup = minNumberOfStudentsPerGroup;

	this->numberOfFitnessNNs = numberOfFitnessNNs;

	this->fitnessCondition = fitnessCondition;

	this->avgAbilities = std::vector<double>(numAdaptationCycles);
	this->avgEngagements = std::vector<double>(numAdaptationCycles);
	this->avgPrefDiff = std::vector<double>(numAdaptationCycles);
	this->avgExecutionTime = 0;

	this->groupSizeFreqs = std::vector<int>(maxNumberOfStudentsPerGroup);
}

std::vector<AdaptationMechanic> Adaptation::iterate(std::vector<Student*> students)
{
	std::vector<AdaptationMechanic> mechanics = std::vector<AdaptationMechanic>();

	adaptedConfig = organizeStudents(students);
	std::vector<AdaptationGroup> groups = adaptedConfig.groups;
	int groupsSize = groups.size();
	for (int i = 0; i < groupsSize; i++) {
		AdaptationGroup currGroup = groups[i];
		std::vector<Student*> groupStudents = currGroup.students;
		int groupStudentsSize = groupStudents.size();

		for (int j = 0; j < groupStudentsSize; j++) {
			Student* currStudent = groupStudents[j];
			currStudent->changeCurrProfile(currGroup.profile);
		}


		Utilities::LearningProfile currGroupProfile = currGroup.profile;
		mechanics.push_back(generateMechanic(currGroupProfile));
	}
	
	return mechanics;
}

AdaptationConfiguration Adaptation::getCurrAdaptedConfig() {
	return this->adaptedConfig;
}

AdaptationConfiguration Adaptation::organizeStudents(std::vector<Student*> students) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = 0.0;


	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		bool lastProfile = false;
		double currFitness = 0.0;
		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(students);
		int studentsSize = students.size();
		AdaptationConfiguration newConfig = AdaptationConfiguration();
		
		
		int numGroups = 1 + rand() % (int)(std::ceil(Globals::students.size() / minNumberOfStudentsPerGroup) - 1);
		
		//generate min groups
		int studentsWithoutGroupSize = 0;
		for (int k = 0; k < numGroups; k++) {
			studentsWithoutGroupSize = studentsWithoutGroup.size();

			AdaptationGroup currGroup = AdaptationGroup();

			//generate learning profile
			double newRand1 = Utilities::randBetween(0, 1);
			double newRand2 = Utilities::randBetween(0, 1);
			double newRand3 = Utilities::randBetween(0, 1);

			double newRandSum = newRand1 + newRand2 + newRand3;

			currGroup.profile.K_cl = newRand1/ newRandSum;
			currGroup.profile.K_cp = newRand2/ newRandSum;
			currGroup.profile.K_i = newRand3/ newRandSum;



			int currStudentIndex = rand() % (studentsWithoutGroupSize - 1);
			for (int s = 0; s < minNumberOfStudentsPerGroup; s++) {
				currGroup.students.push_back(studentsWithoutGroup[currStudentIndex]);
				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			}

			newConfig.groups.push_back(currGroup);
		}

		studentsWithoutGroupSize = studentsWithoutGroup.size();
		while (studentsWithoutGroupSize > 0) {
			int randomGroupIndex = rand() % (newConfig.groups.size());

			int currStudentIndex = 0;
			if (studentsWithoutGroupSize > 1) {
				currStudentIndex = rand() % (studentsWithoutGroupSize);
			}

			AdaptationGroup* currGroup = &newConfig.groups[randomGroupIndex];
			while (currGroup->students.size() > maxNumberOfStudentsPerGroup) {
				currGroup = &newConfig.groups[randomGroupIndex++];
			}

			Student* currStudent = studentsWithoutGroup[currStudentIndex];
			currGroup->students.push_back(currStudent);
			double currStudentFitness = fitness(currStudent, currGroup->profile, this->numberOfFitnessNNs);
			currFitness += currStudentFitness / studentsSize;

			studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			studentsWithoutGroupSize = studentsWithoutGroup.size();
		}

		//generate group for profile
		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
		int m = 0;
		while (m < currGroups->size()) {
			if ((*currGroups)[m].students.size() < 1) {
				(*currGroups).erase((*currGroups).begin() + m);
			}
			else 
			{
				m++;
			}
		}

		//increase this->groupSizeFreqs
		for (int s = 0; s < currGroups->size(); s++) {
			AdaptationGroup currGroup = (*currGroups)[s];
			this->groupSizeFreqs[currGroup.students.size()-1]++;
		}

		if (currFitness > currMaxFitness) {
			bestConfig = newConfig;
			currMaxFitness = currFitness;
		}
	}
	return bestConfig;
}



double Adaptation::fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs) {

	if (fitnessCondition == 0) {
		return Utilities::randBetween(0,1);
	}
	else if(fitnessCondition == 1) {
		double engagement=0;
		double simAbility = student->getAbility();
		student->calcReaction(&engagement, &simAbility, &profile);

		return simAbility;
	}

	std::vector<Student::StudentModel> pastModelIncs = student->getPastModelIncreases();
	std::vector<Student::StudentModel> pastModelncsCopy = std::vector<Student::StudentModel>(pastModelIncs);
	int pastModelIncsSize = pastModelIncs.size();
	
	Student::StudentModel predictedModel = { profile, 0 , 0 };
	std::sort(pastModelncsCopy.begin(), pastModelncsCopy.end(), FitnessSort(this, profile));

	predictedModel.ability = 0;
	predictedModel.engagement = 0;
	for (int i = 0; i < numberOfFitnessNNs; i++) {
		if (i == pastModelIncsSize) {
			break;
		}
		Utilities::LearningProfile pastProfile = pastModelncsCopy[i].currProfile;
		double distance = profile.normalizedDistanceBetween(pastProfile);

		predictedModel.ability += pastModelncsCopy[i].ability * (1.0 - distance) / (double) std::min(pastModelIncsSize, numberOfFitnessNNs);
		predictedModel.engagement += pastModelncsCopy[i].engagement * (1.0 - distance) / (double) std::min(pastModelIncsSize, numberOfFitnessNNs);
	}

	return 0.5*predictedModel.ability + 0.5*predictedModel.engagement;
}

AdaptationMechanic Adaptation::generateMechanic(Utilities::LearningProfile bestConfigProfile) {
	return AdaptationMechanic { "chest" };
}