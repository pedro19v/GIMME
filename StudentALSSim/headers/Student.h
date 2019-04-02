#pragma once
#include <algorithm> 

#include "GlobalStructs.h"
#include "Utilities.h"
#include <iostream>

class Student {
public:
	class StudentModelGrid {
		private:
			std::vector<std::vector<LearningState>> cells;
			int numCells;
			int maxAmountOfStoredProfilesPerCell;

		public:
			StudentModelGrid();
			StudentModelGrid(int numCells, int maxAmountOfStoredProfilesPerCell);
			void pushToGrid(LearningState model);
			std::vector<LearningState> getAllModels();
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
	StudentModelGrid pastModelIncreasesGrid;

	LearningState currModel;

	Utilities* utilities;

public:

	Student(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numIterations, Utilities* utilities);
	void reset(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell);

	void setEngagement(double preference);
	double getEngagement();

	void setAbility(double preference);
	double getAbility();

	std::vector<LearningState> getPastModelIncreases();
	void changeCurrProfile(InteractionsProfile newProfile);

	int getId();
	std::string getName();

	InteractionsProfile getCurrProfile();
	InteractionsProfile getInherentPreference();
	double getLearningRate();

	void simulateReaction(int currIteration);
	void calcReaction(double* engagement, double* ability, InteractionsProfile* profile, int currIteration);



	LearningState currModelIncreases; //for displaying in the chart
};