#pragma once
#include "Headers\User\UserParameter.h"
#include <string>
#include <vector>

class User
{
private:
	std::string userName;
	std::vector<UserParameter> myData;

public:
	User(std::string userName);

	void addParameter(UserParameter userParameter);

};