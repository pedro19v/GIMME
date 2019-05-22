#include "../../headers/Player/Player.h"


Player::PlayerStateGrid::PlayerStateGrid(){}
Player::PlayerStateGrid::PlayerStateGrid(int numCells, int maxAmountOfStoredProfilesPerCell)
{
	this->numCells = numCells;
	this->maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;

	cells = std::vector<std::vector<PlayerState>>(numCells);
}
void Player::PlayerStateGrid::pushToGrid(PlayerState model) {
	double dimSpan = cbrt((double)numCells-1);
	int currCellInd = (int) (dimSpan * dimSpan * floor(dimSpan * model.profile.K_cl) + dimSpan * floor(dimSpan * model.profile.K_cp) + floor(dimSpan* model.profile.K_i));
	/*printf("ind: %d\n", currCellInd);
	printf("profi: (%f,%f,%f)\n", model.currProfile.K_cl, model.currProfile.K_cp, model.currProfile.K_i);*/
	std::vector<PlayerState>* currCell = &(cells[currCellInd]);
	currCell->push_back(model);
	int cellsSize = (int) cells[currCellInd].size();
	if (cellsSize > maxAmountOfStoredProfilesPerCell) {
		currCell->erase(currCell->begin());
	}
}
std::vector<PlayerState> Player::PlayerStateGrid::getAllStates() {
	std::vector<PlayerState> allCells = std::vector<PlayerState>();
	for (int i = 0; i < cells.size(); i++) {
		std::vector<PlayerState>* currCell = &cells[i];
		allCells.insert(allCells.end(), currCell->begin(), currCell->end());
	}
	return allCells;
}



Player::Player(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, RandomGen* utilities){
	this->currState.profile = { 0,0,0 };
	this->currState.characteristics.engagement = 0;
	this->currState.characteristics.ability = 0;

	this->id = id;
	this->name = name;
	this->pastModelIncreasesGrid = PlayerStateGrid(numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell);


	this->numPastModelIncreasesCells = numPastModelIncreasesCells;
	this->maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;

	this->utilities = utilities;
}

void Player::reset(int numberOfPlayerModelCells, int maxAmountOfStoredProfilesPerCell) {
	
	this->currState.profile = { 0,0,0 };

	this->currState.characteristics.engagement = 0;
	this->currState.characteristics.ability = 0;

	this->pastModelIncreasesGrid = PlayerStateGrid(numberOfPlayerModelCells, maxAmountOfStoredProfilesPerCell);
}

PlayerState Player::getCurrState() {
	return this->currState;
}

void Player::setCharacteristics(PlayerCharacteristics characteristics) {
	this->currState.characteristics = characteristics;
}
void Player::setCurrProfile(InteractionsProfile profile) {
	this->currState.profile = profile;
}

std::vector<PlayerState> Player::getPastModelIncreases() {
	return this->pastModelIncreasesGrid.getAllStates();
}


void Player::saveIncreases(PlayerState stateIncreases){
	this->currModelIncreases = stateIncreases;
	this->pastModelIncreasesGrid.pushToGrid(stateIncreases);
}

int Player::getId()
{
	return this->id;
}
std::string Player::getName()
{
	return this->name;
}
InteractionsProfile Player::getCurrProfile() {
	return this->currState.profile;
}


