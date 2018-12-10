#include "../headers/Adaptation.h"

Adaptation::Adaptation(std::vector<Student> students, int numberOfConfigChoices, int maxNumberOfStudentsPerGroup) {
	this->numberOfConfigChoices = numberOfConfigChoices;
	this->maxNumberOfStudentsPerGroup = maxNumberOfStudentsPerGroup;

	this->students = students;
}

std::vector<AdaptationMechanic> Adaptation::iterate()
{
	std::vector<AdaptationMechanic> mechanics = std::vector<AdaptationMechanic>();

	AdaptationConfiguration adaptedConfig = divideStudents(this->students);
	std::vector<AdaptationGroup> groups = adaptedConfig.groups;
	int groupsSize = groups.size();
	for (int i = 0; i < groupsSize; i++) {
		LearningProfile currGroupProfile = groups[i].profile;
		mechanics.push_back(generateMechanic(currGroupProfile));
	}
	return mechanics;
}

AdaptationConfiguration Adaptation::divideStudents(std::vector<Student> students) {

	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = 0.0;

	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < this->numberOfConfigChoices; j++) {
		std::vector<Student> studentsWithoutGroup = std::vector<Student>(students);
		AdaptationConfiguration newConfig = AdaptationConfiguration();

		while (!studentsWithoutGroup.empty()) {
			AdaptationGroup currGroup = AdaptationGroup();
			currGroup.fitness = 0;

			//generate learning profile
			currGroup.profile.K_cl = (double)rand() / (double)(RAND_MAX);
			currGroup.profile.K_cp = (double)rand() / (double)(RAND_MAX);
			currGroup.profile.K_i = (double)rand() / (double)(RAND_MAX);


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
				Student currStudent = studentsWithoutGroup[currStudentIndex];
				currGroup.students.push_back(currStudent);

				double currStudentFitness = currStudent.fitness(currGroup.profile);
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

AdaptationMechanic Adaptation::generateMechanic(LearningProfile bestConfigProfile) {
	return AdaptationMechanic { "chest" };
}