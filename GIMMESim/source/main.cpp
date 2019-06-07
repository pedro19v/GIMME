#include "../headers/GIMMESim.h"


#ifndef GIMME_EXTERNAL_API
#define GIMME_EXTERNAL_API //__declspec(dllexport)
#endif


//extern "C"
//{
RandomGen* randomGen = new RandomGen();
std::vector<Player*>* players = new std::vector<Player*>();
Adaptation* adapt;

void GIMME_EXTERNAL_API addPlayer(int id, char* name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations) {
	Player* player = new Player(id, name, numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell, numStoredPastIterations, randomGen);
	players->push_back(player);
}
void GIMME_EXTERNAL_API removePlayer(int id) {
	//players.erase(players.begin() + players);
}

GIMME_EXTERNAL_API void getPlayerCharacteristics(int id, char* ret) {
	//char ret[] = "";
	std::string playerCharacteristicsStr = std::string();
	for (int i = 0; i < players->size(); i++) {
		Player* currPlayer = (*players)[i];
		if (currPlayer->getId() == id) {
			PlayerCharacteristics charact = currPlayer->getCurrState().characteristics;
			playerCharacteristicsStr += "Ability: " + std::to_string(charact.ability) + "," + "Engagement: " + std::to_string(charact.engagement);
		}
	}
	size_t midSize = (strlen(playerCharacteristicsStr.c_str())+1) * sizeof(char);
	strcpy_s(ret, midSize, playerCharacteristicsStr.c_str());
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

//}


int main() {
	/*std::vector<AdaptationTask> tasks = std::vector<AdaptationTask>();
	GIMMESim sim = GIMMESim(
		100, 50, 30,
		23, 1, 30,
		100, 5, 30,
		2, 5,
		5,
		tasks,
		tasks,
		tasks);
	sim.simulate();*/

	addPlayer(0, (char*) "Name", 1, 1, 30);
	addPlayer(1, (char*) "Name", 1, 1, 30);
	addPlayer(2, (char*) "Name", 1, 1, 30);
	addPlayer(3, (char*) "Name", 1, 1, 30);

	char* test = (char*) malloc(sizeof(char));
	getPlayerCharacteristics(1, test);

	addPlayer(4, (char*) "Name", 1, 1, 30);
}