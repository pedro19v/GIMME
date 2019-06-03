#include "../headers/GIMMECore.h"


#ifndef GIMME_EXTERNAL_API
	#define GIMME_EXTERNAL_API __declspec(dllexport)
#endif		
extern "C"
{
	RandomGen* randomGen;
	std::vector<Player*>* players;
	Adaptation* adapt;

	void GIMME_EXTERNAL_API addPlayer(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations) {
		Player* player = new Player(id, name, numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell, numStoredPastIterations, randomGen);
		players->push_back(player);
	}
	void GIMME_EXTERNAL_API removePlayer(int id) {
		//players.erase(players.begin() + players);
	}
	PlayerCharacteristics GIMME_EXTERNAL_API getPlayerCharacteristics(int id) {
		for (int i = 0; i < players->size(); i++) {
			Player* currPlayer = (*players)[i];
			if (currPlayer->getId() == id) {
				return currPlayer->getCurrState().characteristics;
			}
		}
	}

	void GIMME_EXTERNAL_API initAdaptation() {
		adapt = new Adaptation(
			"test",
			players,
			100,
			2, 5,
			new KNNRegression(5),
			new RandomConfigsGen(),
			new FundamentedFitness(),
			randomGen,
			5);
	}

	void GIMME_EXTERNAL_API iterate() {
		std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> groupMechanicPairs = adapt->iterate();

		//int mechanicsSize = (int)groupMechanicPairs.size();

		////intervene
		//for (int j = 0; j < mechanicsSize; j++) {
		//	std::vector<Player*> currGroup = groupMechanicPairs[j].first.players;
		//	InteractionsProfile currParams = groupMechanicPairs[j].first.interactionsProfile;
		//	std::vector<AdaptationTask> currMechanic = groupMechanicPairs[j].second.tasks;

		//}

		//return groupMechanicPairs;
	}
}