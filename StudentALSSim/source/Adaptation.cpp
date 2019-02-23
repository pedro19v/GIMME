#include "../headers/Adaptation.h"

Adaptation::Adaptation(int studentSize, int numberOfConfigChoices, 
	int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, 
	int numberOfFitnessNNs, int fitnessCondition, int numAdaptationCycles) {

	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;
	this->minNumberOfStudentsPerGroup = minNumberOfStudentsPerGroup;

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

std::vector<AdaptationMechanic> Adaptation::iterate(std::vector<Student*> students, int currIteration)
{
	std::vector<AdaptationMechanic> mechanics = std::vector<AdaptationMechanic>();

	adaptedConfig = organizeStudents(students, currIteration);
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

			currGroup.profile.K_cl = newRand1/ newRandSum;
			currGroup.profile.K_cp = newRand2/ newRandSum;
			currGroup.profile.K_i = newRand3/ newRandSum;



			for (int s = 0; s < minNumberOfStudentsPerGroup; s++) {
				studentsWithoutGroupSize = studentsWithoutGroup.size();
				int currStudentIndex = Utilities::randIntBetween(0,studentsWithoutGroupSize-1);

				Student* currStudent = studentsWithoutGroup[currStudentIndex];
				currGroup.students.push_back(currStudent);

				double currStudentFitness = fitness(currStudent, currGroup.profile, this->numberOfFitnessNNs, currIteration);
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
			while (currGroup->students.size() > maxNumberOfStudentsPerGroup - 1) {
				currGroup = &newConfig.groups[randomGroupIndex++%groupsSize];
			}

			Student* currStudent = studentsWithoutGroup[currStudentIndex];
			currGroup->students.push_back(currStudent);

			double currStudentFitness = fitness(currStudent, currGroup->profile, this->numberOfFitnessNNs, currIteration);
			currFitness += currStudentFitness;

			studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			studentsWithoutGroupSize = studentsWithoutGroup.size();
		}

		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
		this->configSizeFreqs[currGroups->size()]++;
		for (int s = 0; s < currGroups->size(); s++) {
			AdaptationGroup currGroup = (*currGroups)[s];
			this->groupSizeFreqs[currGroup.students.size()]++;
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


//old
//AdaptationConfiguration Adaptation::organizeStudents(std::vector<Student*> students, int currIteration) {
//
//	AdaptationConfiguration bestConfig = AdaptationConfiguration();
//	double currMaxFitness = 0.0;
//
//
//	//generate several random groups, calculate their fitness and select best one
//	for (int j = 0; j < this->numberOfConfigChoices; j++) {
//		bool lastProfile = false;
//		double currFitness = 0.0;
//		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(students);
//		int studentsSize = students.size();
//		AdaptationConfiguration newConfig = AdaptationConfiguration();
//
//		while (!studentsWithoutGroup.empty()) {
//			AdaptationGroup currGroup = AdaptationGroup();
//
//			//generate learning profile
//			double newRand1 = Utilities::randBetween(0, 1);
//			double newRand2 = Utilities::randBetween(0, 1);
//			double newRand3 = Utilities::randBetween(0, 1);
//
//			double newRandSum = newRand1 + newRand2 + newRand3;
//
//			currGroup.profile.K_cl = newRand1 / newRandSum;
//			currGroup.profile.K_cp = newRand2 / newRandSum;
//			currGroup.profile.K_i = newRand3 / newRandSum;
//
//
//			//generate group for profile
//			int studentsWithoutGroupSize = studentsWithoutGroup.size();
//			int currGroupSize = 0;
//			
//			if (studentsWithoutGroupSize > this->minNumberOfStudentsPerGroup) {
//				currGroupSize = Utilities::randIntBetween(this->minNumberOfStudentsPerGroup, std::min(studentsWithoutGroupSize, this->maxNumberOfStudentsPerGroup));
//			}
//			else {
//				for (int i = 0; i < studentsWithoutGroupSize; i++) {
//					newConfig.groups[Utilities::randIntBetween(0, newConfig.groups.size()-1)].students.push_back(studentsWithoutGroup[Utilities::randIntBetween(0, studentsWithoutGroup.size()-1)]);
//				}
//				break;
//			}
//
//			for (int k = 0; k < currGroupSize; k++) {
//				int currStudentIndex = 0;
//				studentsWithoutGroupSize = studentsWithoutGroup.size();
//				if (studentsWithoutGroupSize > 1) {
//					currStudentIndex = Utilities::randIntBetween(0, studentsWithoutGroupSize - 1);
//				}
//				Student* currStudent = studentsWithoutGroup[currStudentIndex];
//				currGroup.addStudent(currStudent);
//
//				double currStudentFitness = fitness(currStudent, currGroup.profile, this->numberOfFitnessNNs, currIteration);
//				currFitness += currStudentFitness / studentsSize;
//
//				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
//			}
//
//			newConfig.groups.push_back(currGroup);
//		}
//
//		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
//		this->configSizeFreqs[currGroups->size()]++;
//		for (int s = 0; s < currGroups->size(); s++) {
//			AdaptationGroup currGroup = (*currGroups)[s];
//			this->groupSizeFreqs[currGroup.students.size()]++;
//		}
//
//		if (fitnessCondition == 0) {
//			return newConfig;
//		}
//
//		if (currFitness > currMaxFitness) {
//			bestConfig = newConfig;
//			currMaxFitness = currFitness;
//		}
//	}
//	return bestConfig;
//}


double Adaptation::fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs, int currIteration) {

	if (fitnessCondition == 1) {
		double engagement = 0;
		double predSimAbility = student->getAbility();

		student->calcReaction(&engagement, &predSimAbility, &profile, currIteration);

		double abilityInc = predSimAbility - student->getAbility();

		return abilityInc;
	}

	std::vector<Student::StudentModel> pastModelIncs = student->getPastModelIncreases();
	std::vector<Student::StudentModel> pastModelncsCopy = std::vector<Student::StudentModel>(pastModelIncs);
	int pastModelIncsSize = pastModelIncs.size();

	Student::StudentModel predictedModel = { profile, 0 , 0 };
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

AdaptationMechanic Adaptation::generateMechanic(Utilities::LearningProfile bestConfigProfile) {
	return AdaptationMechanic { "chest" };
}