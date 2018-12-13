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
	};

	
	double static randBetween(double min, double max) {
		double rand0_1 = (double)rand() / (double)(RAND_MAX);
		return min + rand0_1 * (max - min);
	}
};



