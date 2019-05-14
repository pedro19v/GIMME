#pragma once
#include "../Player/Player.h"

//auxiliary structures: Adaptation
struct AdaptationGroup {
public:
	InteractionsProfile interactionsProfile;
	std::vector<Player*> players;

	InteractionsProfile avgPreferences;
	PlayerState avgLearningState;

	void addPlayer(Player* player) {
		players.push_back(player);
		int playersSize = (int)players.size();

		//recalculate averages
		avgLearningState = PlayerState();
		avgPreferences.K_cl = 0;
		avgPreferences.K_cp = 0;
		avgPreferences.K_i = 0;

		for (int i = 0; i < playersSize; i++) {
			Player* currPlayer = players[i];
			//InteractionsProfile currPlayerPreference = currPlayer->getInherentPreference();
			avgLearningState.characteristics.engagement += currPlayer->getCurrState().characteristics.engagement / playersSize;
			avgLearningState.characteristics.ability += currPlayer->getCurrState().characteristics.ability / playersSize;
			/*avgPreferences.K_cl += currPlayerPreference.K_cl / PlayersSize;
			avgPreferences.K_cp += currPlayerPreference.K_cp / PlayersSize;
			avgPreferences.K_i += currPlayerPreference.K_i / PlayersSize;*/
		}
	}
};
struct AdaptationConfiguration {
public:
	std::vector<AdaptationGroup> groups;
};
enum AdaptationTaskType {
	COLLABORATION = 0,
	COMPETITION = 1,
	SELF_INTERACTION = 2,
	NONE = 3
};
struct AdaptationTask {
	AdaptationTaskType type;
	std::string description;
	float minRequiredAbility;
	std::vector<AdaptationTask> taskInstances; //maintained in order
};
struct AdaptationMechanic {
public:
	InteractionsProfile profile;
	std::vector<AdaptationTask> tasks;
};
