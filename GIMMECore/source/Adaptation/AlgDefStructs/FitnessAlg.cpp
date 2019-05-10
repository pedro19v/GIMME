#include "../../../headers/Adaptation/AlgDefStructs/FitnessAlg.h"

double RandomFitness::calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg regAlg)
{
	return 0.0;
}

double SimulationsOptimalFitness::calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg regAlg)
{
	/*double engagement = student->getCurrState().characteristics.engagement;
		double ability = student->getCurrState().characteristics.ability;*/
	PlayerState predictedState = PlayerState(player->getCurrState());

	//((SimStudent*)student)->calcReaction(&predictedState, currIteration);
	double abilityInc = predictedState.characteristics.ability - player->getCurrState().characteristics.ability;
	return abilityInc;
}

double FundamentedFitness::calculate(Player* player, InteractionsProfile interactionsProfile, RegressionAlg regAlg)
{
	FitnessSort sort = FitnessSort(interactionsProfile);
	PlayerState predictedModel = regAlg.predict(interactionsProfile, player, &sort);
	return 0.5*(predictedModel.characteristics.ability) + 0.5*predictedModel.characteristics.engagement; //ability must be normalized to [0,1]
}
