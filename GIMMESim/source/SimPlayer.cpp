#include "../headers/SimPlayer.h"

SimPlayer::SimPlayer(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, RandomGen* utilities): Player( id, name, numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell, numStoredPastIterations, utilities) {

	//generate learning profile
	double newRand1 = utilities->randBetween(0, 1);
	double newRand2 = utilities->randBetween(0, 1);
	double newRand3 = utilities->randBetween(0, 1);

	double newRandSum = newRand1 + newRand2 + newRand3;

	this->inherentPreference.K_cl = newRand1 / newRandSum;
	this->inherentPreference.K_cp = newRand2 / newRandSum;
	this->inherentPreference.K_i = newRand3 / newRandSum;

	this->baseLearningRate = utilities->randBetween(0.2, 0.6);
	this->iterationReactions = std::vector<double>(numStoredPastIterations);
	
	for (int i = 0; i < numStoredPastIterations; i++) {
		this->iterationReactions[i] = utilities->normalRandom(baseLearningRate, 0.05);
	}

	
	this->inherentPreference = inherentPreference;
	this->baseLearningRate = baseLearningRate;
	this->iterationReactions = std::vector<double>(numStoredPastIterations);

	for (int i = 0; i < numStoredPastIterations; i++) {
		this->iterationReactions[i] = utilities->normalRandom(baseLearningRate, 0.05);
	}
}

InteractionsProfile SimPlayer::getInherentPreference() {
	return this->inherentPreference;
}
double SimPlayer::getLearningRate() {
	return this->baseLearningRate;
}

void SimPlayer::simulateReaction(int currIteration)
{
	PlayerState increases = PlayerState(currState);
	this->calcReaction(&currState, currIteration);

	increases.characteristics = {(currState.characteristics.ability - increases.characteristics.ability), currState.characteristics.engagement };
	
	this->saveIncreases(increases);
}

void SimPlayer::calcReaction(PlayerState* state, int currIteration)
{
	InteractionsProfile currProfile = this->currState.profile;

	(*state).characteristics.engagement = 0.5* ((*state).characteristics.engagement) + 0.5* (1.0 - inherentPreference.distanceBetween((*state).profile));

	double currTaskReaction = iterationReactions[currIteration];
	double abilityIncreaseSim = (currTaskReaction * (*state).characteristics.engagement); //between 0 and 1
	(*state).characteristics.ability += abilityIncreaseSim;
}