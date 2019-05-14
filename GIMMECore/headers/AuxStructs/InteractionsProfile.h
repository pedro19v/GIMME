#pragma once
#include <cmath>

struct InteractionsProfile {
public:
	double K_i;
	double K_cp;
	double K_cl;

	double normalizedDistanceBetween(InteractionsProfile profileToTest)
	{
		InteractionsProfile profile1 = *this;
		InteractionsProfile cost = { 0,0,0 };
		//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = std::abs(profile1.K_cl - profileToTest.K_cl);
		cost.K_cp = std::abs(profile1.K_cp - profileToTest.K_cp);
		cost.K_i = std::abs(profile1.K_i - profileToTest.K_i);

		double totalDiff = cost.K_cl + cost.K_cp + cost.K_i;

		cost.K_cl /= totalDiff;
		cost.K_cp /= totalDiff;
		cost.K_i /= totalDiff;

		cost.K_cl = std::pow(cost.K_cl, 2);
		cost.K_cp = std::pow(cost.K_cl, 2);
		cost.K_i = std::pow(cost.K_cl, 2);

		return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
	}

	double distanceBetween(InteractionsProfile profileToTest)
	{
		InteractionsProfile profile1 = *this;
		InteractionsProfile cost = { 0,0,0 };
		//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = std::abs(profile1.K_cl - profileToTest.K_cl);
		cost.K_cp = std::abs(profile1.K_cp - profileToTest.K_cp);
		cost.K_i = std::abs(profile1.K_i - profileToTest.K_i);


		cost.K_cl = std::pow(cost.K_cl, 2);
		cost.K_cp = std::pow(cost.K_cl, 2);
		cost.K_i = std::pow(cost.K_cl, 2);

		return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
	}
};