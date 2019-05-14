#pragma once
#include <algorithm> 

#include "..\AuxStructs\RandomGen.h"
#include "PlayerStructs.h"


#include <iostream>
#include <string>

class Player {
public:
	class PlayerStateGrid {
		private:
			std::vector<std::vector<PlayerState>> cells;
			int numCells;
			int maxAmountOfStoredProfilesPerCell;

		public:
			PlayerStateGrid();
			PlayerStateGrid(int numCells, int maxAmountOfStoredProfilesPerCell);
			void pushToGrid(PlayerState model);
			std::vector<PlayerState> getAllStates();
	};

protected:
	int id;
	std::string name;

	//Adaptation part
	int numPastModelIncreasesCells;
	int maxAmountOfStoredProfilesPerCell;
	PlayerStateGrid pastModelIncreasesGrid;

	PlayerState currState;
	RandomGen* utilities;

	void saveIncreases(PlayerState stateIncreases);
public:

	Player(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, RandomGen* utilities);
	
	void reset(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell);


	std::vector<PlayerState> getPastModelIncreases();
	PlayerState getCurrState();

	void setCharacteristics(PlayerCharacteristics characteristics);
	void setCurrProfile(InteractionsProfile profile);
	
	int getId();
	std::string getName();

	InteractionsProfile getCurrProfile();
	

	PlayerState currModelIncreases; //for displaying in the chart

};