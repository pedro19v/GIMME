#include "../../../headers/Adaptation/AlgDefStructs/RegressionAlg.h"

//---------------------- KNNRegression stuff ---------------------------
KNNRegression::KNNRegression(int numberOfNNs)
{
	this->numberOfNNs = numberOfNNs;
}

PlayerState KNNRegression::predict(InteractionsProfile profile, Player* player)
{
	std::vector<PlayerState> pastModelIncs = player->getPastModelIncreases();
	std::vector<PlayerState> pastModelncsCopy = std::vector<PlayerState>(pastModelIncs);
	int pastModelIncsSize = (int)pastModelIncs.size();

	PlayerState predictedModel = { profile, 0 , 0 };
	std::sort(pastModelncsCopy.begin(), pastModelncsCopy.end(), InteractionsProfileSort(profile));

	if (pastModelIncsSize > numberOfNNs) {
		pastModelncsCopy.resize(numberOfNNs);
	}
	int pastModelncsCopySize = (int)pastModelncsCopy.size();

	for (int i = 0; i < pastModelncsCopySize; i++) {
		InteractionsProfile pastProfile = pastModelncsCopy[i].profile;
		double distance = profile.distanceBetween(pastProfile);

		predictedModel.characteristics.ability += (pastModelncsCopy[i].characteristics.ability* (1 - distance)) / (double)(pastModelncsCopySize); //* (1 - distance) 
		predictedModel.characteristics.engagement += (pastModelncsCopy[i].characteristics.engagement* (1 - distance)) / (double)(pastModelncsCopySize); //* (1 - distance)
	}

	return predictedModel;
}



//---------------------- NeuralNetworkRegression stuff ---------------------------

NeuralNetworkRegression::NeuralNetworkRegression()
{
}

PlayerState NeuralNetworkRegression::predict(InteractionsProfile profile, Player* player)
{
	PlayerState predictedModel = { profile, 0 , 0 };

	return predictedModel;
}



//---------------------- ReinforcementLearningRegression stuff ---------------------------

ReinforcementLearningRegression::ReinforcementLearningRegression()
{
}

PlayerState ReinforcementLearningRegression::predict(InteractionsProfile profile, Player* player)
{
	PlayerState predictedModel = { profile, 0 , 0 };

	return predictedModel;
}