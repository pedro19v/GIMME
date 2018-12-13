#include "../headers/Student.h"





Student::Student(int id, std::string name) {
	this->inherentPreference = { Utilities::randBetween(0,1), Utilities::randBetween(0,1), Utilities::randBetween(0,1) };
	this->learningRate = Utilities::randBetween(0, 1);

	this->myModel.currProfile = { 0,0,0 };

	this->myModel.preference = 0;
	this->myModel.ability = 0;

	this->id = id;
	this->name = name;
	this->pastModels = std::vector<StudentModel>();
}

void Student::setPreference(double preference) {
	this->myModel.preference = preference;
}
double Student::getPreference() {
	return this->myModel.preference;
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
