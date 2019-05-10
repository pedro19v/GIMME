#pragma once
#include "FitnessAlg.h"
#include "../AdaptationStructs.h"

class ConfigsGenAlg
{
public:
	std::vector<int> groupSizeFreqs;
	std::vector<int> configSizeFreqs;

	AdaptationConfiguration organize(std::vector<Player*>* players, int numberOfConfigChoices, int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, RandomGen* utilities, RegressionAlg regAlg, FitnessAlg fitAlg) {
		int playersSize = (int)players->size();
		this->groupSizeFreqs = std::vector<int>(playersSize + 1);
		this->configSizeFreqs = std::vector<int>(playersSize + 1);

		return AdaptationConfiguration();
	};

	void updateMetrics(AdaptationConfiguration generatedConfig) {
		configSizeFreqs[generatedConfig.groups.size()]++;
		for(AdaptationGroup group : generatedConfig.groups) {
			groupSizeFreqs[group.getPlayers().size()]++;
		}
	};
};

class RandomConfigsGen : public ConfigsGenAlg {
public:
	AdaptationConfiguration organize(std::vector<Player*>* players, int numberOfConfigChoices, int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, RandomGen* utilities, RegressionAlg regAlg, FitnessAlg fitAlg);
};

class EvolutionaryConfigsGen : public ConfigsGenAlg {
public:
	AdaptationConfiguration organize(std::vector<Player*>* players, int numberOfConfigChoices, int minNumberOfStudentsPerGroup, int maxNumberOfStudentsPerGroup, RandomGen* utilities, RegressionAlg regAlg, FitnessAlg fitAlg);
};
