#pragma once
#include <vector>
#include <random>
#include "string.h"

#define _USE_MATH_DEFINES


class Utilities {
public:
	static int defaultRandomSeed;

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

	
	double static randBetween(int seed, double min, double max) {
		srand(seed);
		double rand0_1 = (double)rand() / (double)(RAND_MAX);
		return min + rand0_1 * (max - min);
	}
	double static randBetween(double min, double max) {
		return randBetween(defaultRandomSeed, min, max);
	}

	double static normalRandom(int seed, double mu, double var) {

		static std::default_random_engine normalRandomGenerator (seed);
		std::normal_distribution<double> distribution(mu, var);
		return distribution(normalRandomGenerator);
	}
	double static normalRandom(double mu, double var) {
		return normalRandom(defaultRandomSeed, mu, var);
	}
};

