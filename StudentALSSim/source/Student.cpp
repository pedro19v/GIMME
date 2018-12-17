#include "../headers/Student.h"



Student::Student(int id, std::string name, int maxAmountOfStoredProfiles) {
	this->inherentPreference = { Utilities::randBetween(0, 1), Utilities::randBetween(0, 1), Utilities::randBetween(0, 1) };
	this->learningRate = Utilities::randBetween(0, 1);

	this->myModel.currProfile = { 0,0,0 };

	this->myModel.engagement = 0;
	this->myModel.ability = 0;

	this->id = id;
	this->name = name;
	this->pastModels = std::vector<StudentModel>();

	this->maxAmountOfStoredProfiles = maxAmountOfStoredProfiles;
}

void Student::reset() {
	
	this->myModel.currProfile = { 0,0,0 };

	this->myModel.engagement = 0;
	this->myModel.ability = 0;

	this->pastModels = std::vector<StudentModel>();
}

void Student::setEngagement(double engagement) {
	this->myModel.engagement = engagement;
}
double Student::getEngagement() {
	return this->myModel.engagement;
}

std::vector<Student::StudentModel> Student::getPastModels() {
	return this->pastModels;
}


void Student::setAbility(double ability) {
	this->myModel.ability = ability;
}
double Student::getAbility() {
	return this->myModel.ability;
}


void Student::changeCurrProfile(Utilities::LearningProfile currProfile) {
	this->pastModels.push_back(this->myModel);
	if (this->pastModels.size() > maxAmountOfStoredProfiles) {
		this->pastModels.erase(this->pastModels.begin());
	}
	this->myModel.currProfile = currProfile;
}
Utilities::LearningProfile Student::getCurrProfile() {
	return this->myModel.currProfile;
}
Utilities::LearningProfile Student::getInherentPreference() {
	return this->inherentPreference;
}
double Student::getLearningRate() {
	return this->learningRate;
}

void Student::simulateReaction(int numberOfAdaptationCycles)
{
	Utilities::LearningProfile currProfile = this->myModel.currProfile;

	double onOffTaskSim = 1 - inherentPreference.distanceBetween(currProfile);
	this->myModel.engagement = onOffTaskSim;

	double abilityIncreaseSim = (learningRate * onOffTaskSim); //between 0 and 1
	this->myModel.ability += abilityIncreaseSim;
}
