#include "../headers/ConfigsGenAlg.h"

//AdaptationConfiguration RandomGen::organize(std::vector<Student*> students)
//{
//	AdaptationConfiguration bestConfig = AdaptationConfiguration();
//	double currMaxFitness = -INFINITY;
//
//
//	//generate several random groups, calculate their fitness and select best one
//	for (int j = 0; j < this->numberOfConfigChoices; j++) {
//		bool lastProfile = false;
//		double currFitness = 0.0;
//		std::vector<Student*> studentsWithoutGroup = std::vector<Student*>(*students);
//		int studentsSize = (int)students->size();
//		AdaptationConfiguration newConfig = AdaptationConfiguration();
//
//		int minNumGroups = (int)ceil((double)students->size() / (double)maxNumberOfStudentsPerGroup);
//		int maxNumGroups = (int)floor((double)students->size() / (double)minNumberOfStudentsPerGroup);
//		int numGroups = utilities->randIntBetween(minNumGroups, maxNumGroups);
//
//		//generate min groups
//		int studentsWithoutGroupSize = 0;
//		for (int k = 0; k < numGroups; k++) {
//
//			AdaptationGroup currGroup = AdaptationGroup();
//
//			//generate learning profile
//			double newRand1 = utilities->randBetween(0, 1);
//			double newRand2 = utilities->randBetween(0, 1);
//			double newRand3 = utilities->randBetween(0, 1);
//
//			double newRandSum = newRand1 + newRand2 + newRand3;
//
//			InteractionsProfile profile = InteractionsProfile();
//			profile.K_cl = newRand1 / newRandSum;
//			profile.K_cp = newRand2 / newRandSum;
//			profile.K_i = newRand3 / newRandSum;
//			currGroup.setInteractionsProfile(profile);
//
//
//			for (int s = 0; s < minNumberOfStudentsPerGroup; s++) {
//				studentsWithoutGroupSize = (int)studentsWithoutGroup.size();
//				int currStudentIndex = utilities->randIntBetween(0, studentsWithoutGroupSize - 1);
//
//				Student* currStudent = studentsWithoutGroup[currStudentIndex];
//				currGroup.addStudent(currStudent);
//
//				double currStudentFitness = fitness(currStudent, currGroup.getInteractionsProfile(), currIteration);
//				currFitness += currStudentFitness;
//
//				studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
//			}
//
//			newConfig.groups.push_back(currGroup);
//		}
//
//		studentsWithoutGroupSize = (int)studentsWithoutGroup.size();
//		while (studentsWithoutGroupSize > 0) {
//			int randomGroupIndex = utilities->randIntBetween(0, (int)newConfig.groups.size() - 1);
//
//			int currStudentIndex = 0;
//			if (studentsWithoutGroupSize > 1) {
//				currStudentIndex = utilities->randIntBetween(0, studentsWithoutGroupSize - 1);
//			}
//
//			AdaptationGroup* currGroup = &newConfig.groups[randomGroupIndex];
//			int groupsSize = (int)newConfig.groups.size();
//			while ((int)currGroup->getStudents().size() > maxNumberOfStudentsPerGroup - 1) {
//				currGroup = &newConfig.groups[randomGroupIndex++%groupsSize];
//			}
//
//			Student* currStudent = studentsWithoutGroup[currStudentIndex];
//			currGroup->addStudent(currStudent);
//
//			double currStudentFitness = fitness(currStudent, currGroup->getInteractionsProfile(), currIteration);
//			currFitness += currStudentFitness;
//
//			studentsWithoutGroup.erase(studentsWithoutGroup.begin() + currStudentIndex);
//			studentsWithoutGroupSize = (int)studentsWithoutGroup.size();
//		}
//
//		int studentSize = students->size();
//		this->groupSizeFreqs.resize(studentSize + 1);
//		this->configSizeFreqs.resize(studentSize + 1);
//		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
//		int currGroupsSize = (int)currGroups->size();
//		this->configSizeFreqs[currGroupsSize]++;
//		for (int s = 0; s < currGroupsSize; s++) {
//			AdaptationGroup currGroup = (*currGroups)[s];
//			this->groupSizeFreqs[(int)currGroup.getStudents().size()]++;
//		}
//
//		//return random config when fitnessCondition = 0
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