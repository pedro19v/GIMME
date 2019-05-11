#include "../../../headers/Adaptation/AlgDefStructs/ConfigsGenAlg.h"

AdaptationConfiguration RandomConfigsGen::organize(std::vector<Player*>* players, int numberOfConfigChoices, int minNumberOfPlayersPerGroup, int maxNumberOfPlayersPerGroup, RandomGen* randomGen, RegressionAlg* regAlg, FitnessAlg* fitAlg)
{
	AdaptationConfiguration bestConfig = AdaptationConfiguration();
	double currMaxFitness = -INFINITY;


	//generate several random groups, calculate their fitness and select best one
	for (int j = 0; j < numberOfConfigChoices; j++) {
		bool lastProfile = false;
		double currFitness = 0.0;
		std::vector<Player*> playersWithoutGroup = std::vector<Player*>(*players);
		int PlayersSize = (int)players->size();
		AdaptationConfiguration newConfig = AdaptationConfiguration();

		int minNumGroups = (int)ceil((double)players->size() / (double)maxNumberOfPlayersPerGroup);
		int maxNumGroups = (int)floor((double)players->size() / (double)minNumberOfPlayersPerGroup);
		int numGroups = randomGen->randIntBetween(minNumGroups, maxNumGroups);

		//generate min groups
		int playersWithoutGroupSize = 0;
		for (int k = 0; k < numGroups; k++) {

			AdaptationGroup currGroup = AdaptationGroup();

			//generate learning profile
			double newRand1 = randomGen->randBetween(0, 1);
			double newRand2 = randomGen->randBetween(0, 1);
			double newRand3 = randomGen->randBetween(0, 1);

			double newRandSum = newRand1 + newRand2 + newRand3;

			InteractionsProfile profile = InteractionsProfile();
			profile.K_cl = newRand1 / newRandSum;
			profile.K_cp = newRand2 / newRandSum;
			profile.K_i = newRand3 / newRandSum;
			currGroup.setInteractionsProfile(profile);


			for (int s = 0; s < minNumberOfPlayersPerGroup; s++) {
				playersWithoutGroupSize = (int)playersWithoutGroup.size();
				int currPlayerIndex = randomGen->randIntBetween(0, playersWithoutGroupSize - 1);

				Player* currPlayer = playersWithoutGroup[currPlayerIndex];
				currGroup.addPlayer(currPlayer);

				//double currPlayerFitness = fitAlg.calculate(currPlayer, currGroup.getInteractionsProfile());
				double currPlayerFitness = fitAlg->calculate(currPlayer, currGroup.getInteractionsProfile(), regAlg);
				currFitness += currPlayerFitness;

				playersWithoutGroup.erase(playersWithoutGroup.begin() + currPlayerIndex);
			}

			newConfig.groups.push_back(currGroup);
		}

		playersWithoutGroupSize = (int)playersWithoutGroup.size();
		while (playersWithoutGroupSize > 0) {
			int randomGroupIndex = randomGen->randIntBetween(0, (int)newConfig.groups.size() - 1);

			int currPlayerIndex = 0;
			if (playersWithoutGroupSize > 1) {
				currPlayerIndex = randomGen->randIntBetween(0, playersWithoutGroupSize - 1);
			}

			AdaptationGroup* currGroup = &newConfig.groups[randomGroupIndex];
			int groupsSize = (int)newConfig.groups.size();
			while ((int)currGroup->getPlayers().size() > maxNumberOfPlayersPerGroup - 1) {
				currGroup = &newConfig.groups[randomGroupIndex++%groupsSize];
			}

			Player* currPlayer = playersWithoutGroup[currPlayerIndex];
			currGroup->addPlayer(currPlayer);

			double currPlayerFitness = fitAlg->calculate(currPlayer, currGroup->getInteractionsProfile(), regAlg);
			//double currPlayerFitness = fitAlg.calculate(currPlayer, currGroup->getInteractionsProfile());
			currFitness += currPlayerFitness;

			playersWithoutGroup.erase(playersWithoutGroup.begin() + currPlayerIndex);
			playersWithoutGroupSize = (int)playersWithoutGroup.size();
		}

		int PlayerSize = players->size();
		this->groupSizeFreqs.resize(PlayerSize + 1);
		this->configSizeFreqs.resize(PlayerSize + 1);
		std::vector<AdaptationGroup>* currGroups = &newConfig.groups;
		int currGroupsSize = (int)currGroups->size();
		this->configSizeFreqs[currGroupsSize]++;
		for (int s = 0; s < currGroupsSize; s++) {
			AdaptationGroup currGroup = (*currGroups)[s];
			this->groupSizeFreqs[(int)currGroup.getPlayers().size()]++;
		}


		if (currFitness > currMaxFitness) {
			bestConfig = newConfig;
			currMaxFitness = currFitness;
		}
	}
	updateMetrics(bestConfig);
	return bestConfig;
}