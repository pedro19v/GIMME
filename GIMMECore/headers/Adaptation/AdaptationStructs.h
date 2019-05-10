#pragma once
#include "../Player/Player.h"

//auxiliary structures: Adaptation
struct AdaptationGroup {
private:
	PlayerState avgLearningState;
	InteractionsProfile avgPreferences;
	InteractionsProfile interactionsProfile;
	std::vector<Player*> players;

public:

	void addPlayer(Player* Player) {
		players.push_back(Player);
		int PlayersSize = (int)players.size();

		//recalculate averages
		avgLearningState = PlayerState();
		avgPreferences.K_cl = 0;
		avgPreferences.K_cp = 0;
		avgPreferences.K_i = 0;

		//for (int i = 0; i < PlayersSize; i++) {
		//	Player* currPlayer = players[i];
		//	//InteractionsProfile currPlayerPreference = currPlayer->getInherentPreference();
		//	avgLearningState.characteristics.engagement += currPlayer->getCurrState().characteristics.engagement / PlayersSize;
		//	avgLearningState.characteristics.ability += currPlayer->getCurrState().characteristics.ability / PlayersSize;
		//	/*avgPreferences.K_cl += currPlayerPreference.K_cl / PlayersSize;
		//	avgPreferences.K_cp += currPlayerPreference.K_cp / PlayersSize;
		//	avgPreferences.K_i += currPlayerPreference.K_i / PlayersSize;*/
		//}
	}
	std::vector<Player*> getPlayers() {
		return this->players;
	}
	void setInteractionsProfile(InteractionsProfile learningProfile) {
		this->interactionsProfile = learningProfile;
	}

	InteractionsProfile getInteractionsProfile() {
		return this->interactionsProfile;
	}
	PlayerState getAvgLearningState() {
		return this->avgLearningState;
	}
	InteractionsProfile getAvgPreferences() {
		return this->avgPreferences;
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
private:
	/*struct WayToSortTaskInstances {
		bool operator()(const AdaptationTask& i, const AdaptationTask& j) { return i.minRequiredAbility < j.minRequiredAbility; }
	};*/
public:
	AdaptationTaskType type;
	std::string description;
	float minRequiredAbility;
	std::vector<AdaptationTask> taskInstances; //maintained in order

	AdaptationTask(AdaptationTaskType type, std::string description, float minRequiredAbility, std::vector<AdaptationTask> taskInstances) {
		this->type = type;
		this->description = description;
		this->minRequiredAbility = minRequiredAbility;

		//std::sort(taskInstances.begin(), taskInstances.end(), WayToSortTaskInstances());
		this->taskInstances = taskInstances;
	}
	AdaptationTask(AdaptationTaskType type, std::string description, std::vector<AdaptationTask> taskInstances) : AdaptationTask(type, description, 0, taskInstances) {}
	AdaptationTask(AdaptationTaskType type, std::string description, float minRequiredAbility) : AdaptationTask(type, description, minRequiredAbility, std::vector<AdaptationTask>()) {}
};
struct AdaptationMechanic {
public:
	InteractionsProfile profile;
	std::vector<AdaptationTask> tasks;
};
