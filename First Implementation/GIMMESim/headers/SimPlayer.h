#pragma once

#include "../../GIMMECore/headers/GIMMECore.h"

class SimPlayer: public Player {

private:
	//for simulation
	InteractionsProfile inherentPreference;
	double baseLearningRate;
	std::vector<double> iterationReactions;
public:

	SimPlayer(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, RandomGen* utilities); //for simulations

	InteractionsProfile getInherentPreference();
	double getLearningRate();

	void simulateReaction(int currIteration);
	void calcReaction(PlayerState* state, int currIteration);
};