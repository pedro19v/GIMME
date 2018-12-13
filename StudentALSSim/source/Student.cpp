#include "../headers/Student.h"

Student::Student(int id, std::string name) {
	this->inherentPreference = { Utilities::randBetween(0,1), Utilities::randBetween(0,1), Utilities::randBetween(0,1) };
	this->learningRate = Utilities::randBetween(0, 1);

	this->currProfile = { 0,0,0 };

	this->preference = 0;
	this->ability = 0;

	this->id = id;
	this->name = name;
	this->pastLearningProfiles = std::vector<Utilities::LearningProfile>();
}
double Student::fitness(Utilities::LearningProfile profile) {

	return rand() / (double)RAND_MAX;
}

void Student::setPreference(double preference) {
	this->preference = preference;
}
double Student::getPreference() {
	return this->preference;
}



void Student::setAbility(double ability) {
	this->ability = ability;
}
double Student::getAbility() {
	return this->ability;
}


void Student::setCurrProfile(Utilities::LearningProfile currProfile) {
	this->currProfile = currProfile;
}
Utilities::LearningProfile Student::getCurrProfile() {
	return this->currProfile;
}
Utilities::LearningProfile Student::getInherentPreference() {
	return this->inherentPreference;
}
double Student::getLearningRate() {
	return this->learningRate;
}