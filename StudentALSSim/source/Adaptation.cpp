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
		Utilities::LearningProfile currGroupProfile = groups[i].profile;
		mechanics.push_back(generateMechanic(currGroupProfile));
	}
	return mechanics;
}

AdaptationConfiguration Adaptation::divideStudents(std::vector<Student*> students) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = 0.0;

	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(students);
		AdaptationConfiguration newConfig = AdaptationConfiguration();

		while (!studentsWithoutGroup.empty()) {
			AdaptationGroup currGroup = AdaptationGroup();
			currGroup.fitness = 0;

			double learningProfileTotal = 1.0;
			//generate learning profile
			double newRand = Utilities::randBetween(0,1);
			learningProfileTotal -= newRand;
			currGroup.profile.K_cl = newRand;

			newRand = Utilities::randBetween(newRand, 1);
			learningProfileTotal -= newRand;
			currGroup.profile.K_cp = newRand;

			currGroup.profile.K_i = learningProfileTotal;


			//append students
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
				currStudent->changeCurrProfile(currGroup.profile);

				double currStudentFitness = fitness(currStudent,currGroup.profile,this->numberOfFitnessNNs);
				currGroup.fitness += currStudentFitness / currGroupSize;

				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
			}

			newConfig.groups.push_back(currGroup);
		}

		std::vector<AdaptationGroup> currConfigGroups = newConfig.groups;
		int currConfigGroupsSize = currConfigGroups.size();
		for (int k = 0; k < currConfigGroupsSize; k++) {
			newConfig.fitness += currConfigGroups[k].fitness / currConfigGroupsSize;
		}

		if (newConfig.fitness >= currMaxFitness) {
			bestConfig = newConfig;
		}
		return bestConfig;
	}
}

double Adaptation::fitness(Student* student, Utilities::LearningProfile profile, int numberOfFitnessNNs) {

	if (isRandomFitness) {
		return rand() / (double)RAND_MAX;
	}

	std::vector<Student::StudentModel> pastModels = student->getPastModels();
	int pastModelsSize = pastModels.size();
	std::sort(pastModels.begin(), pastModels.end(), FitnessSort(student));

	Student::StudentModel predictedModel = { profile, 0 , 0};
	for (int i = 0; i < numberOfFitnessNNs; i++) {
		if (i > pastModelsSize) {
			break;
		}
		Student::StudentModel currModel = pastModels[i];
		predictedModel.ability += currModel.ability / numberOfFitnessNNs;
		predictedModel.preference += currModel.preference / numberOfFitnessNNs;
	}
	return 0.5*predictedModel.ability + 0.5*predictedModel.preference;
}

AdaptationMechanic Adaptation::generateMechanic(Utilities::LearningProfile bestConfigProfile) {
	return AdaptationMechanic { "chest" };
}