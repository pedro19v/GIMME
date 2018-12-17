#pragma once
#include <vector>
#include "string.h"

#define _USE_MATH_DEFINES

class Utilities {
public:
		
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

		double distanceBetween(Utilities::LearningProfile profile2)
		{
			Utilities::LearningProfile profile1 = *this;
			Utilities::LearningProfile cost = { 0,0,0 };
			cost.K_cl = std::pow((profile1.K_cl - profile2.K_cl), 2);
			cost.K_cp = std::pow((profile1.K_cp - profile2.K_cp), 2);
			cost.K_i = std::pow((profile1.K_i - profile2.K_i), 2);
			return cost.K_cl + cost.K_cp + cost.K_i;
		}

	};

	
	double static randBetween(double min, double max) {
		double rand0_1 = (double)rand() / (double)(RAND_MAX);
		return min + rand0_1 * (max - min);
	}
};



