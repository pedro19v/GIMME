#pragma once

#include "../../GIMMECore/headers/GIMMECore.h"

class SimStudent: public Student {

private:
	//for simulation
	InteractionsProfile inherentPreference;
	double baseLearningRate;
	std::vector<double> iterationReactions;
public:

	SimStudent(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, Utilities* utilities); //for simulations

	InteractionsProfile getInherentPreference();
	double getLearningRate();

	void simulateReaction(int currIteration);
	void calcReaction(PlayerState* state, int currIteration);
};