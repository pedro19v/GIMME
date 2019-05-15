#pragma once
#include "../../AuxStructs/RandomGen.h"
#include "RegressionAlg.h"

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