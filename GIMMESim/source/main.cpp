#include "../headers/GIMMESim.h"
#include "../../GIMMECore/source/GIMMECore.cpp"


int main() {
	/*std::vector<AdaptationTask> tasks = std::vector<AdaptationTask>();
	GIMMESim sim = GIMMESim(
		100, 50, 30,
		23, 1, 30,
		100, 5, 30,
		2, 5,
		5,
		tasks,
		tasks,
		tasks);
	sim.simulate();*/

	addPlayer(0, (char*) "Name", 1, 1, 30);
	addPlayer(1, (char*) "Name", 1, 1, 30);
	addPlayer(2, (char*) "Name", 1, 1, 30);
	addPlayer(3, (char*) "Name", 1, 1, 30);
	initAdaptation();
	iterate();

	getPlayerCharacteristics(1);

	addPlayer(4, (char*) "Name", 1, 1, 30);
}