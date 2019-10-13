#include "..//..//headers//AuxStructs//RandomGen.h"

RandomGen::RandomGen() {
	this->defaultRandomSeed = (int) time(NULL);
	this->uniformDistributionReal = std::uniform_real_distribution<double>();
	this->uniformDistributionInt = std::uniform_int_distribution<>();
	this->normalDistribution = std::normal_distribution<double>();
}


void RandomGen::resetRandoms() {
	uniformDistributionReal.reset();
	normalDistribution.reset();
}
double RandomGen::randBetween(int seed, double min, double max) {
	static std::default_random_engine randomGenerator(seed);
	uniformDistributionReal = std::uniform_real_distribution<double>(min, max);
	return uniformDistributionReal(randomGenerator);
}
double RandomGen::randBetween(double min, double max) {
	return randBetween(defaultRandomSeed, min, max);
}

int RandomGen::randIntBetween(int seed, int min, int max) {
	static std::default_random_engine randomGenerator(seed);
	uniformDistributionInt = std::uniform_int_distribution<>(min, max);
	return uniformDistributionInt(randomGenerator);
}
int RandomGen::randIntBetween(int min, int max) {
	return randIntBetween(defaultRandomSeed, min, max);
}

double RandomGen::normalRandom(int seed, double mu, double var) {
	static std::default_random_engine normalRandomGenerator(seed);
	normalDistribution = std::normal_distribution<double>(mu, var);
	return normalDistribution(normalRandomGenerator);
}
double RandomGen::normalRandom(double mu, double var) {
	return normalRandom(defaultRandomSeed, mu, var);
}


