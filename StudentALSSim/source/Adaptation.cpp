#include "../headers/Adaptation.h"

Adaptation::Adaptation(int numberOfConfigChoices, int maxNumberOfStudentsPerGroup, int numberOfFitnessNNs, bool isRandomFitness) {
	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;

	this->numberOfFitnessNNs = numberOfFitnessNNs;

	this->isRandomFitness = isRandomFitness;
}

std::vector<AdaptationMechanic> Adaptation::iterate(std::vector<Student*> students)
{
	std::vector<AdaptationMechanic> mechanics = std::vector<AdaptationMechanic>();

	AdaptationConfiguration adaptedConfig = divideStudents(students);
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

AdaptationConfiguration Adaptation::divideStudents(std::vector<Student*> students) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = 0.0;

	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		double currFitness = 0.0;
		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(students);
		int studentsSize = students.size();
		AdaptationConfiguration newConfig = AdaptationConfiguration();

		while (!studentsWithoutGroup.empty()) {
			AdaptationGroup currGroup = AdaptationGroup();

			//generate learning profile
			double newRand1 = Utilities::randBetween(0, 1);
			double newRand2 = Utilities::randBetween(0, 1);
			double newRand3 = Utilities::randBetween(0, 1);

			double newRandSum = newRand1 + newRand2 + newRand3;

			currGroup.profile.K_cl = newRand1/ newRandSum;
			currGroup.profile.K_cp = newRand2/ newRandSum;
			currGroup.profile.K_i = newRand3/ newRandSum;


			//generate group for profile
			int studentsWithoutGroupSize = studentsWithoutGroup.size();
			int currGroupSize = 0;
			if (studentsWithoutGroupSize > 1) {
				currGroupSize = 1 + rand() % (std::min(studentsWithoutGroupSize, this->maxNumberOfStudentsPerGroup) - 1);
			}
			else {
				currGroupSize = 1;
			}
			for (int k = 0; k < currGroupSize; k++) {
				int currStudentIndex = 0;
				studentsWithoutGroupSize = studentsWithoutGroup.size();
				if (studentsWithoutGroupSize > 1) {
					currStudentIndex = rand() % (studentsWithoutGroupSize - 1);
				}
				Student* currStudent = studentsWithoutGroup[currStudentIndex];
				currGroup.students.push_back(currStudent);

				double currStudentFitness = fitness(currStudent, currGroup.profile, this->numberOfFitnessNNs);
				currFitness += currStudentFitness / studentsSize;

				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			}

			newConfig.groups.push_back(currGroup);
		}

		if (currFitness > currMaxFitness) {
			bestConfig = newConfig;
			currMaxFitness = currFitness;
		}
	}
	return bestConfig;
}



double Adaptation::fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs) {

	if (isRandomFitness) {
		return Utilities::randBetween(0,1);
	}

	std::vector<Student::StudentModel> pastModels = student->getPastModels();
	int pastModelsSize = pastModels.size();
	
	Student::StudentModel predictedModel = { profile, 0 , 0 };
	std::sort(pastModels.begin(), pastModels.end(), FitnessSort(this, profile));
	for (int i = 0; i < numberOfFitnessNNs; i++) {
		if (i == pastModelsSize) {
			break;
		}
		Utilities::LearningProfile pastProfile = pastModels[i].currProfile;
		double distance = profile.distanceBetween(pastProfile);

		predictedModel.ability +=  student->getAbility() * (1 - distance) / (double) std::min(pastModelsSize, numberOfFitnessNNs);
		predictedModel.engagement += student->getEngagement() * (1 - distance) / (double) std::min(pastModelsSize, numberOfFitnessNNs);
	}

	//double onOffTaskSim = profile.K_cl*student->getInherentPreference().K_cl
	//	+ profile.K_cp*student->getInherentPreference().K_cp
	//	+ profile.K_i*student->getInherentPreference().K_i;
	//predictedModel.preference = onOffTaskSim;

	//double abilityIncreaseSim = (student->getLearningRate() * onOffTaskSim) / 1000; //between 0 and 1
	//predictedModel.ability = student->getAbility() + abilityIncreaseSim;

	return 0.5*predictedModel.ability + 0.5*predictedModel.engagement;
}

AdaptationMechanic Adaptation::generateMechanic(Utilities::LearningProfile bestConfigProfile) {
	return AdaptationMechanic { "chest" };
}