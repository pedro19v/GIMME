#include "Headers\User\User.h"

User::User(std::string userName)
{
	this->userName = userName;
}

void User::addParameter(UserParameter userParameter)
{
	this->myData.push_back(userParameter);
}
