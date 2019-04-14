#include "../headers/Student.h"


Student::StudentStateGrid::StudentStateGrid(){}
Student::StudentStateGrid::StudentStateGrid(int numCells, int maxAmountOfStoredProfilesPerCell)
{
	this->numCells = numCells;
	this->maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;

	cells = std::vector<std::vector<PlayerState>>(numCells);
}
void Student::StudentStateGrid::pushToGrid(PlayerState model) {
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
std::vector<PlayerState> Student::StudentStateGrid::getAllStates() {
	std::vector<PlayerState> allCells = std::vector<PlayerState>();
	for (int i = 0; i < cells.size(); i++) {
		std::vector<PlayerState>* currCell = &cells[i];
		allCells.insert(allCells.end(), currCell->begin(), currCell->end());
	}
	return allCells;
}


Student::Student(int id, std::string name, int numPastModelIncreasesCells, int maxAmountOfStoredProfilesPerCell, int numStoredPastIterations, Utilities* utilities){
	
	//generate learning profile
	double newRand1 = utilities->randBetween(0, 1);
	double newRand2 = utilities->randBetween(0, 1);
	double newRand3 = utilities->randBetween(0, 1);

	double newRandSum = newRand1 + newRand2 + newRand3;

	this->inherentPreference.K_cl = newRand1 / newRandSum;
	this->inherentPreference.K_cp = newRand2 / newRandSum;
	this->inherentPreference.K_i = newRand3 / newRandSum;

	this->learningRate = utilities->randBetween(0.2, 0.6);
	this->iterationReactions = std::vector<double>(numStoredPastIterations);

	for (int i = 0; i < numStoredPastIterations; i++) {
		this->iterationReactions[i] = utilities->normalRandom(learningRate, 0.05);
	}

	//this->learningRate = Utilities::randBetween(0, 1);

	this->currState.profile = { 0,0,0 };
	this->currState.characteristics.engagement = 0;
	this->currState.characteristics.ability = 0;

	this->id = id;
	this->name = name;
	this->pastModelIncreasesGrid = StudentStateGrid(numPastModelIncreasesCells, maxAmountOfStoredProfilesPerCell);


	this->numPastModelIncreasesCells = numPastModelIncreasesCells;
	this->maxAmountOfStoredProfilesPerCell = maxAmountOfStoredProfilesPerCell;

	this->utilities = utilities;
}

void Student::reset(int numberOfStudentModelCells, int maxAmountOfStoredProfilesPerCell) {
	
	this->currState.profile = { 0,0,0 };

	this->currState.characteristics.engagement = 0;
	this->currState.characteristics.ability = 0;

	this->pastModelIncreasesGrid = StudentStateGrid(numberOfStudentModelCells, maxAmountOfStoredProfilesPerCell);
}

PlayerState Student::getCurrState() {
	return this->currState;
}
void Student::setCharacteristics(PlayerCharacteristics characteristics) {
	this->currState.characteristics = characteristics;
}

std::vector<PlayerState> Student::getPastModelIncreases() {
	return this->pastModelIncreasesGrid.getAllStates();
}


void Student::setCurrProfile(InteractionsProfile newProfile){
	
	//save past profiles
	PlayerState increases = PlayerState(currState);

	increases.characteristics.ability = currState.characteristics.ability - increases.characteristics.ability;
	increases.characteristics.engagement = currState.characteristics.engagement; // -increases.engagement;

	this->pastModelIncreasesGrid.pushToGrid(increases);

	this->currState.profile = newProfile;
}
int Student::getId()
{
	return this->id;
}
std::string Student::getName()
{
	return this->name;
}
InteractionsProfile Student::getCurrProfile() {
	return this->currState.profile;
}
InteractionsProfile Student::getInherentPreference() {
	return this->inherentPreference;
}
double Student::getLearningRate() {
	return this->learningRate;
}

void Student::simulateReaction(int currIteration)
{
	PlayerState increases = PlayerState(currState);
	this->calcReaction(&currState.characteristics.engagement, &currState.characteristics.ability, &currState.profile, currIteration);

	increases.characteristics.ability = currState.characteristics.ability - increases.characteristics.ability;
	increases.characteristics.engagement = currState.characteristics.engagement; // -increases.engagement;

	this->pastModelIncreasesGrid.pushToGrid(increases);
}

void Student::calcReaction(double* engagement, double* ability, InteractionsProfile* profile, int currIteration)
{
	InteractionsProfile currProfile = this->currState.profile;

	*engagement = 0.5* (*engagement) + 0.5* (1.0 - inherentPreference.distanceBetween(*profile));

	double currTaskReaction = iterationReactions[currIteration];
	double abilityIncreaseSim = (currTaskReaction * *engagement); //between 0 and 1
	*ability += abilityIncreaseSim;
}
