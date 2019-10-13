#pragma once
#include "..//..//Player//Player.h"

struct InteractionsProfileSort {
	InteractionsProfile testedProfile;

	InteractionsProfileSort(InteractionsProfile testedProfile) {
		this->testedProfile = testedProfile;
	}

	bool operator () (PlayerState& i, PlayerState& j) {

		double dist1 = testedProfile.distanceBetween(i.profile);
		double dist2 = testedProfile.distanceBetween(j.profile);

		i.dist = dist1;
		j.dist = dist2;

		return dist1 < dist2;
	}
};

class RegressionAlg
{
public:
	virtual PlayerState predict(InteractionsProfile profile, Player* player) = 0;
};

class KNNRegression: public RegressionAlg {
private:
	int numberOfNNs;
public:
	KNNRegression(int numberOfNNs);
	PlayerState predict(InteractionsProfile profile, Player* player);
};


class NeuralNetworkRegression : public RegressionAlg {
private:
public:
	NeuralNetworkRegression();
	PlayerState predict(InteractionsProfile profile, Player* player);
};


class ReinforcementLearningRegression : public RegressionAlg {
private:
	double value;
	//double pMatrix[][];


public:
	ReinforcementLearningRegression();
	PlayerState predict(InteractionsProfile profile, Player* player);
};