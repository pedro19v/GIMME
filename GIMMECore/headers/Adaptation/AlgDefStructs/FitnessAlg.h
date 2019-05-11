#pragma once
#include "../../AuxStructs/RandomGen.h"
#include "RegressionAlg.h"

struct FitnessSort {
	InteractionsProfile testedProfile;

	FitnessSort(InteractionsProfile testedProfile) {
		this->testedProfile = testedProfile;
	}

	bool operator () (PlayerState& i, PlayerState& j) {

		double dist1 = testedProfile.distanceBetween(i.profile);
		double dist2 = testedProfile.distanceBetween(j.profile);

		i.dist = dist1;
		j.dist = dist2;

		return dist1 < dist2;
	}
};

class FitnessAlg
{
public:
	virtual double calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg* regAlg) = 0;
};

class RandomFitness : public FitnessAlg {
public:
	double calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg* regAlg);
};

class SimulationsOptimalFitness : public FitnessAlg {
public:
	double calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg* regAlg);
};

class FundamentedFitness : public FitnessAlg {
public:
	double calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg* regAlg);
};