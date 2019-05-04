#pragma once
#include "Student.h"

class IRegressionAlg
{
public:
	PlayerState predict(InteractionsProfile profile, Student* student, void* sortFunc) { return PlayerState(); };
};

class KNNRegression: public IRegressionAlg {
private:
	int numberOfNNs;
public:
	KNNRegression(int numberOfNNs);
	PlayerState predict(InteractionsProfile profile, Student* student, void* sortFunc);
};


class NeuralNetworkRegression : public IRegressionAlg {
private:
public:
	NeuralNetworkRegression();
	PlayerState predict(InteractionsProfile profile, Student* student, void* sortFunc);
};


class ReinforcementLearningRegression : public IRegressionAlg {
private:
	double value;
	//double pMatrix[][];


public:
	ReinforcementLearningRegression();
	PlayerState predict(InteractionsProfile profile, Student* student, void* sortFunc);
};