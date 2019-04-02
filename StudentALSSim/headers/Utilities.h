#pragma once
#include <vector>
#include <random>
#include "string.h"

#define _USE_MATH_DEFINES

//struct AdaptationTask; //forward declaration

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

	double randIntBetween(int seed, int min, int max);
	double randIntBetween(int min, int max);

	template <class c>
	void randShuffle(std::vector<c>& vector);

	double normalRandom(int seed, double mu, double var);
	double normalRandom(double mu, double var);
};

