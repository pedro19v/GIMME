#pragma once
#include "Headers\User\User.h"
#include "Headers\ContentProfile.h"
#include <string>
#include <map>
#include <vector>

class Manager
{
private:	
	std::map<std::string,User*> applicationUsers;

public:
	ContentProfile calcContentProfile();
	void addUser(User* user);

	User* getUserByName(std::string username);

};