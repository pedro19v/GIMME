#pragma once
#include "Headers\User\UserParameter.h"
#include "Headers\ContentProfile.h"
#include <string>
#include <map>

class User
{
private:
	std::string userName;
	std::map<std::string, UserParameter*> myData;

public:
	User(std::string userName);
	User();

	std::string getName();
	std::vector<UserParameter*> getMyData(); //retrieves all UserParameters and builds a vector with them. Not to be used often!
	void addParameter(UserParameter* userParameter);
	UserParameter* getParameterByName(std::string parameterName);

	ContentProfile calcUserContentProfile();
};