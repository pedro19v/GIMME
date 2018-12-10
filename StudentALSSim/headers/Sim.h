#pragma once
#include <vector>
#include "string.h"

#define _USE_MATH_DEFINES

struct LearningProfile {
public:
	double K_i;
	double K_cp;
	double K_cl;

	LearningProfile(double K_i, double K_cp, double K_cl)
	{
		this->K_i = K_i;
		this->K_cp = K_cp;
		this->K_cl = K_cl;
	}

	LearningProfile()
	{
		this->K_i = 0.0;
		this->K_cp = 0.0;
		this->K_cl = 0.0;
	}
};


class Student {
private:
	int id;
	std::string name;


	//Adaptation part

	double preference; //percentage
	double ability; //percentage

	std::vector<LearningProfile> pastLearningProfiles;
	int amountOfStoredProfiles;

public:
	Student(int id, std::string name) {

		this->preference = 0;
		this->ability = 0;

		this->id = id;
		this->name = name;
		this->pastLearningProfiles = std::vector<LearningProfile>();
	}
	double fitness(LearningProfile profile) {
		return rand() / (double)RAND_MAX;
	}

	void setPreference(double preference) {
		this->preference = preference;
	}
	void setAbility(double preference) {
		this->ability = ability;
	}

	double getPreference() {
		return this->preference;
	}
	double getAbility() {
		return this->ability;
	}
};



