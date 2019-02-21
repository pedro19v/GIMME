#pragma once
#include <vector>
#include <random>
#include "string.h"

#define _USE_MATH_DEFINES

struct AdaptationTask; //forward declaration

class Utilities {
public:

	static int defaultRandomSeed;
	static std::normal_distribution<double> normalDistribution;
	static std::uniform_real_distribution<double> uniformDistributionReal;
	static std::uniform_int_distribution<> uniformDistributionInt;


	struct LearningProfile {
		public:
		double K_i;
		double K_cp;
		double K_cl;

		LearningProfile(double K_i, double K_cp, double K_cl)
		{
			this->K_i = K_i;
			this->K_cp = K_cp;
			this->K_cl = K_cl;
		}

		LearningProfile()
		{
			this->K_i = 0.0;
			this->K_cp = 0.0;
			this->K_cl = 0.0;
		}

		double normalizedDistanceBetween(Utilities::LearningProfile profile2)
		{
			Utilities::LearningProfile profile1 = *this;
			Utilities::LearningProfile cost = { 0,0,0 };
			//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
			cost.K_cl = std::abs(profile1.K_cl - profile2.K_cl);
			cost.K_cp = std::abs(profile1.K_cp - profile2.K_cp);
			cost.K_i = std::abs(profile1.K_i - profile2.K_i);

			double totalDiff = cost.K_cl + cost.K_cp + cost.K_i;

			cost.K_cl /= totalDiff;
			cost.K_cp /= totalDiff;
			cost.K_i /= totalDiff;

			cost.K_cl = std::pow(cost.K_cl, 2);
			cost.K_cp = std::pow(cost.K_cl, 2);
			cost.K_i = std::pow(cost.K_cl, 2);

			return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
		}

		double distanceBetween(Utilities::LearningProfile profile2)
		{
			Utilities::LearningProfile profile1 = *this;
			Utilities::LearningProfile cost = { 0,0,0 };
			//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
			cost.K_cl = std::abs(profile1.K_cl - profile2.K_cl);
			cost.K_cp = std::abs(profile1.K_cp - profile2.K_cp);
			cost.K_i = std::abs(profile1.K_i - profile2.K_i);


			cost.K_cl = std::pow(cost.K_cl, 2);
			cost.K_cp = std::pow(cost.K_cl, 2);
			cost.K_i = std::pow(cost.K_cl, 2);

			return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
		}

	};

	
	void static resetRandoms() {
		uniformDistributionReal.reset();
		normalDistribution.reset();
	}
	double static randBetween(int seed, double min, double max) {
		static std::default_random_engine randomGenerator(seed);
		uniformDistributionReal = std::uniform_real_distribution<double>(min, max);
		return uniformDistributionReal(randomGenerator);
	}
	double static randBetween(double min, double max) {
		return randBetween(defaultRandomSeed, min, max);
	}

	double static randIntBetween(int seed, int min, int max) {
		static std::default_random_engine randomGenerator(seed);
		uniformDistributionInt = std::uniform_int_distribution<>(min, max);
		return uniformDistributionInt(randomGenerator);
	}
	double static randIntBetween(int min, int max) {
		return randIntBetween(defaultRandomSeed, min, max);
	}

	/*template <class c>
	void static randShuffle(std::vector<c> vector) {
		shuffle(vector.begin(), vector.end(), uniformDistributionInt);
	}*/

	double static normalRandom(int seed, double mu, double var) {
		static std::default_random_engine normalRandomGenerator (seed);
		normalDistribution = std::normal_distribution<double>(mu, var);
		return normalDistribution(normalRandomGenerator);
	}
	double static normalRandom(double mu, double var) {
		return normalRandom(defaultRandomSeed, mu, var);
	}
};

