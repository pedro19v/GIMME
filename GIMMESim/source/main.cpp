#include "../headers/GIMMESim.h"

int main() {
	std::vector<AdaptationTask> tasks = std::vector<AdaptationTask>();
	GIMMESim sim = GIMMESim(
		20, 300, 30,
		23, 1, 5,
		100, 5, 30,
		2, 5,
		5,
		tasks,
		tasks,
		tasks);
	sim.simulate();
}