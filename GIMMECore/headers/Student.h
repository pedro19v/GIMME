#pragma once
#include <algorithm> 

#include "Utilities.h"
#include <iostream>


struct InteractionsProfile {
public:
	double K_i;
	double K_cp;
	double K_cl;

	InteractionsProfile(double K_i, double K_cp, double K_cl)
	{
		this->K_i = K_i;
		this->K_cp = K_cp;
		this->K_cl = K_cl;
	}

	InteractionsProfile()
	{
		this->K_i = 0.0;
		this->K_cp = 0.0;
		this->K_cl = 0.0;
	}

	double normalizedDistanceBetween(InteractionsProfile profile2)
	{
		InteractionsProfile profile1 = *this;
		InteractionsProfile cost = { 0,0,0 };
		//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = std::abs(profile1.K_cl - profile2.K_cl);
		cost.K_cp = std::abs(profile1.K_cp - profile2.K_cp);
		cost.K_i = std::abs(profile1.K_i - profile2.K_i);

		double totalDiff = cost.K_cl + cost.K_cp + cost.K_i;

		cost.K_cl /= totalDiff;
		cost.K_cp /= totalDiff;
		cost.K_i /= totalDiff;

		cost.K_cl = std::pow(cost.K_cl, 2);
		cost.K_cp = std::pow(cost.K_cl, 2);
		cost.K_i = std::pow(cost.K_cl, 2);

		return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
	}

	double distanceBetween(InteractionsProfile profile2)
	{
		InteractionsProfile profile1 = *this;
		InteractionsProfile cost = { 0,0,0 };
		//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = std::abs(profile1.K_cl - profile2.K_cl);
		cost.K_cp = std::abs(profile1.K_cp - profile2.K_cp);
		cost.K_i = std::abs(profile1.K_i - profile2.K_i);


		cost.K_cl = std::pow(cost.K_cl, 2);
		cost.K_cp = std::pow(cost.K_cl, 2);
		cost.K_i = std::pow(cost.K_cl, 2);

		return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
	}

};

struct LearningState {
	InteractionsProfile profile;
	double engagement; // on vs off task percentage
	double ability; // score percentage

	double dist;
};


class Student {
public:
	class StudentStateGrid {
		private:
			std::vector<std::vector<LearningState>> cells;
			int numCells;
			int maxAmountOfStoredProfilesPerCell;

		public:
			StudentStateGrid();
			StudentStateGrid(int numCells, int maxAmountOfStoredProfilesPerCell);
			void pushToGrid(LearningState model);
			std::vector<LearningState> getAllStates();
	};

private:
	int id;
	std::string name;

	//for simulation
	InteractionsProfile inherentPreference;
	double learningRate;
	std::vector<double> iterationReactions;

	//Adaptation part
	int numPastModelIncreasesCells;
	int maxAmountOfStoredProfilesPerCell;
	StudentStateGrid pastModelIncreasesGrid;

	LearningState currState;
	Utilities* utilities;

public:

	Student(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, Utilities* utilities);
	void reset(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell);


	std::vector<LearningState> getPastModelIncreases();
	LearningState getCurrState();
	void setCurrProfile(InteractionsProfile newProfile);

	int getId();
	std::string getName();

	InteractionsProfile getCurrProfile();
	InteractionsProfile getInherentPreference();
	double getLearningRate();

	void simulateReaction(int currIteration);
	void calcReaction(double* engagement, double* ability, InteractionsProfile* profile, int currIteration);

	LearningState currModelIncreases; //for displaying in the chart
};