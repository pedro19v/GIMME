#include "../headers/GIMMECore.h"


#ifndef GIMME_EXTERNAL_API
#define GIMME_EXTERNAL_API __declspec(dllexport)
#endif

struct ExportedAdaptationGroup {
public:
	InteractionsProfile interactionsProfile;
	int* playerIDs;

	//AdaptationMechanic tailoredMechanic;

	PlayerCharacteristics avgPlayerCharacteristics;

};

struct ExportedAdaptationConfiguration {
public:
	ExportedAdaptationGroup* groups;
};



extern "C"
{
	RandomGen* randomGen;
	std::vector<Player*>* players;
	Adaptation* adapt;

	void GIMME_EXTERNAL_API addPlayer(int id, char* name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations) {
		Player* player = new Player(id, name, numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell, numStoredPastIterations, randomGen);
		players->push_back(player);
	}
	void GIMME_EXTERNAL_API removePlayer(int id) {
		//players.erase(players.begin() + players);
	}

	PlayerCharacteristics GIMME_EXTERNAL_API getPlayerCharacteristics(int id) {
		std::string playerCharacteristicsStr = std::string();
		for (int i = 0; i < players->size(); i++) {
			Player* currPlayer = (*players)[i];
			if (currPlayer->getId() == id) {
				PlayerCharacteristics charact = currPlayer->getCurrState().characteristics;
				return charact;
			}
		}
	}

	void GIMME_EXTERNAL_API setPlayerCharacteristics(int id, PlayerCharacteristics characteristics) {
		std::string playerCharacteristicsStr = std::string();
		for (int i = 0; i < players->size(); i++) {
			Player* currPlayer = (*players)[i];
			if (currPlayer->getId() == id) {
				currPlayer->setCharacteristics(characteristics);
			}
		}
	}

	void GIMME_EXTERNAL_API initAdaptation() {
		randomGen = new RandomGen();
		players = new std::vector<Player*>();
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

	ExportedAdaptationConfiguration GIMME_EXTERNAL_API iterate() {
		AdaptationConfiguration groupMechanicPairs = adapt->iterate();

		ExportedAdaptationConfiguration exportedConfig;
		exportedConfig.groups = (ExportedAdaptationGroup*) malloc(sizeof(ExportedAdaptationGroup)*players->size());
		for (int i = 0; i < (groupMechanicPairs.groups).size(); i++) {
			AdaptationGroup currGroup = (groupMechanicPairs.groups)[i];
			int size = currGroup.players.size();
			int* playerIDs = (int*) malloc(sizeof(int)* size);
			for (int i = 0; i < size; i++) {
				Player currPlayer = *(currGroup.players[i]);
				playerIDs[i] = currPlayer.getId();
			}

			ExportedAdaptationGroup exportedGroup = {
				currGroup.interactionsProfile,
				playerIDs,
				currGroup.avgPlayerState.characteristics
			};
			exportedConfig.groups[i] = exportedGroup;
		}

		return exportedConfig;
	}
}