#pragma once
#include <vector>
#include <random>
#include "string.h"
#include "time.h"

#define _USE_MATH_DEFINES

class Utilities {
	
public:
	
	int defaultRandomSeed;
	std::normal_distribution<double> normalDistribution;
	std::uniform_real_distribution<double> uniformDistributionReal;
	std::uniform_int_distribution<> uniformDistributionInt;

	Utilities();
	
	void resetRandoms();
	double randBetween(int seed, double min, double max);
	double randBetween(double min, double max);

	int randIntBetween(int seed, int min, int max);
	int randIntBetween(int min, int max);

	template <class c>
	inline void randShuffle(std::vector<c>& vector);

	double normalRandom(int seed, double mu, double var);
	double normalRandom(double mu, double var);
};

#include "../source/Utilities.inl"