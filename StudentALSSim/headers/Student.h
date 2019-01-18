#pragma once
#include <algorithm> 

#include "Utilities.h"
#include <iostream>

class Student {
public:
	struct StudentModel {
		Utilities::LearningProfile currProfile;
		double engagement; // on vs off task percentage
		double ability; // score percentage

		double dist;
	};
	
	class StudentModelGrid {
		private:
			std::vector<std::vector<StudentModel>> cells;
			int numCells;
			int maxAmountOfStoredProfilesPerCell;

		public:
			StudentModelGrid();
			StudentModelGrid(int numCells, int maxAmountOfStoredProfilesPerCell);
			void pushToGrid(StudentModel model);
			std::vector<StudentModel> getAllModels();
	};


private:
	int id;
	std::string name;

	//for simulation
	Utilities::LearningProfile inherentPreference;
	double learningRate;
	double learningRateSeed;

	//Adaptation part
	int numPastModelIncreasesCells;
	int maxAmountOfStoredProfilesPerCell;
	StudentModelGrid pastModelIncreasesGrid;

	StudentModel currModel;
	

public:

	Student(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell);
	void reset(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell);

	void setEngagement(double preference);
	double getEngagement();

	void setAbility(double preference);
	double getAbility();

	std::vector<StudentModel> getPastModelIncreases();
	void changeCurrProfile(Utilities::LearningProfile newProfile);


	Utilities::LearningProfile getCurrProfile();
	Utilities::LearningProfile getInherentPreference();
	double getLearningRate();

	void simulateReaction();
	void calcReaction(double* engagement, double* ability, Utilities::LearningProfile* profile);
};