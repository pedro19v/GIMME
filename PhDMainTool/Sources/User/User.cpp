#include "Headers\User\User.h"

User::User()
{
	this->userName = "default";
}

User::User(std::string userName)
{
	this->userName = userName;
}

std::string User::getName()
{
	return this->userName;
}

std::vector<UserParameter*> User::getMyData()
{
	std::vector<UserParameter*> allValues = std::vector<UserParameter*>();
	for (std::map<std::string, UserParameter*>::iterator it = myData.begin(); it != myData.end(); ++it) {
		allValues.push_back(it->second);
	}
	return allValues;
}


UserParameter* User::getParameterByName(std::string parameterName)
{
	std::map<std::string, UserParameter*>::iterator it;
	it = myData.find(parameterName);
	if (it != myData.end()) {
		return it->second;
	}
	std::printf("[ERROR] user parameter with name %s not found", parameterName.c_str());
	std::abort();
}

void User::addParameter(UserParameter* userParameter)
{
	this->myData[userParameter->getName()] = userParameter;
}

ContentProfile User::calcUserContentProfile()
{
	return ContentProfile();
}
