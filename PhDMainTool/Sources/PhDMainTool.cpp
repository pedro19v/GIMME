#include "Headers\User\User.h"
#include "Headers\User\UserParameter.h"
#include "Headers\ContentProfile.h"

#include <stdio.h>

int main()
{
	User sam = User("Sam");
	User tiago = User("Tiago");

	UserParameter numJumps = UserParameter(0, 100, "numJumps");

	sam.addParameter(numJumps);

	ContentProfile::competitionPercentage = 0.3f;

	numJumps.setValue(20);


	std::printf("numJumps:%f\n",numJumps.getValue());

	std::getchar();

	return 0;
}