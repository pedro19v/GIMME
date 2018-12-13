#pragma once
#include "Utilities.h"

class Student {
private:
	int id;
	std::string name;

	//for simulation
	Utilities::LearningProfile inherentPreference;
	double learningRate;

	//Adaptation part
	Utilities::LearningProfile currProfile;

	double preference; // on vs off task percentage
	double ability; // score percentage

	std::vector<Utilities::LearningProfile> pastLearningProfiles;
	int amountOfStoredProfiles;

public:
	Student(int id, std::string name);
	double fitness(Utilities::LearningProfile profile);

	void setPreference(double preference);
	double getPreference();

	void setAbility(double preference);
	double getAbility();


	void setCurrProfile(Utilities::LearningProfile currProfile);
	Utilities::LearningProfile getCurrProfile();
	Utilities::LearningProfile getInherentPreference();
	double getLearningRate();
};