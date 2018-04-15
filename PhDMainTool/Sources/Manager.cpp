#include "Headers\Manager.h"

ContentProfile Manager::calcContentProfile()
{
	return ContentProfile();
}

void Manager::addUser(User* user) {
	this->applicationUsers[user->getName()] = user;
}

User* Manager::getUserByName(std::string username)
{
	std::map<std::string, User*>::iterator it;
	it = applicationUsers.find(username);
	if (it != applicationUsers.end()) {
		return it->second;
	}
	std::printf("[ERROR] user with name %s not found", username.c_str());
	std::abort();
}
