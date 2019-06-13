#include "../headers/GIMMECore.h"


#ifndef GIMME_EXTERNAL_API
#define GIMME_EXTERNAL_API __declspec(dllexport)
#endif

extern "C"
{


	RandomGen* randomGen;
	std::vector<Player*>* players;
	Adaptation* adapt;

	const int MAX_NUM_GROUPS = 50;
	const int MAX_GROUPS_SIZE = 5;

struct ExportedAdaptationGroup {
public:
	InteractionsProfile interactionsProfile;

	int numPlayers;
	int playerIDs[MAX_GROUPS_SIZE];

	//AdaptationMechanic tailoredMechanic;

	PlayerCharacteristics avgPlayerCharacteristics;
};

struct ExportedAdaptationConfiguration {
public:
	int numGroups;
	ExportedAdaptationGroup groups[MAX_NUM_GROUPS];
};


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
			2, MAX_GROUPS_SIZE,
			new KNNRegression(5),
			new RandomConfigsGen(),
			new FundamentedFitness(),
			randomGen,
			5);
	}

	ExportedAdaptationConfiguration GIMME_EXTERNAL_API iterate() {
		AdaptationConfiguration groupMechanicPairs = adapt->iterate();

		ExportedAdaptationConfiguration exportedConfig;
		exportedConfig.numGroups = (groupMechanicPairs.groups).size();
		//exportedConfig.groups = (ExportedAdaptationGroup*) malloc(sizeof(ExportedAdaptationGroup)*players->size());
		for (int i = 0; i < MAX_NUM_GROUPS; i++) {
			if (i >= (groupMechanicPairs.groups).size()) {
				exportedConfig.groups[i] = ExportedAdaptationGroup();
				continue;
			}
			AdaptationGroup currGroup = (groupMechanicPairs.groups)[i];
			int size = currGroup.players.size();

			ExportedAdaptationGroup exportedGroup;
			
			exportedGroup.interactionsProfile = currGroup.interactionsProfile;
			exportedGroup.avgPlayerCharacteristics = currGroup.avgPlayerState.characteristics;
			exportedGroup.numPlayers = size;
			for (int i = 0; i < MAX_GROUPS_SIZE; i++) {
				if (i >= size) {
					exportedGroup.playerIDs[i] = -1;
					continue;
				}
				Player currPlayer = *(currGroup.players[i]);
				exportedGroup.playerIDs[i] = currPlayer.getId();
			}

			exportedConfig.groups[i] = exportedGroup;
		}

		return exportedConfig;
	}
}