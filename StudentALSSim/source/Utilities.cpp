#include "..\headers\Utilities.h"
#include "Utilities.h"

#define _USE_MATH_DEFINES

//struct AdaptationTask; //forward declaration

Utilities::Utilities() {
	this.defaultRandomSeed = time(NULL);
	this.uniformDistributionReal = std::uniform_real_distribution<double>();
	this.uniformDistributionInt = std::uniform_int_distribution<>();
	this.normalDistribution = std::normal_distribution<double>();
}


void Utilities::resetRandoms() {
	uniformDistributionReal.reset();
	normalDistribution.reset();
}
double Utilities::randBetween(int seed, double min, double max) {
	static std::default_random_engine randomGenerator(seed);
	uniformDistributionReal = std::uniform_real_distribution<double>(min, max);
	return uniformDistributionReal(randomGenerator);
}
double Utilities::randBetween(double min, double max) {
	return randBetween(defaultRandomSeed, min, max);
}

double Utilities::randIntBetween(int seed, int min, int max) {
	static std::default_random_engine randomGenerator(seed);
	uniformDistributionInt = std::uniform_int_distribution<>(min, max);
	return uniformDistributionInt(randomGenerator);
}
double Utilities::randIntBetween(int min, int max) {
	return randIntBetween(defaultRandomSeed, min, max);
}

template <class c>
void Utilities::randShuffle(std::vector<c>& vector) {
	static std::default_random_engine randomGenerator(defaultRandomSeed);
	shuffle(vector.begin(), vector.end(), randomGenerator);
}

double Utilities::normalRandom(int seed, double mu, double var) {
	static std::default_random_engine normalRandomGenerator(seed);
	normalDistribution = std::normal_distribution<double>(mu, var);
	return normalDistribution(normalRandomGenerator);
}
double Utilities::normalRandom(double mu, double var) {
	return normalRandom(defaultRandomSeed, mu, var);
}


