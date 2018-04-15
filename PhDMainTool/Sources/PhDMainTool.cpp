#include "Headers\User\User.h"
#include "Headers\User\UserParameter.h"
#include "Headers\ContentProfile.h"
#include "Headers\Manager.h"

#include <stdio.h>

int main()
{
	Manager genManager = Manager();


	User* sam = new User("Sam");
	genManager.addUser(sam);

	UserParameter* numJumpsSam = new UserParameter(0, 100, "numJumps");
	sam->addParameter(numJumpsSam);

	numJumpsSam->setValue(20);

	User* tiago = new User("Tiago");
	genManager.addUser(tiago);


	std::printf("%s: %f\n", genManager.getUserByName("Sam")->getName().c_str(), genManager.getUserByName("Sam")->getParameterByName("numJumps")->getValue());

	std::getchar();

	return 0;
}


