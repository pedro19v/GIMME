#include "../headers/GIMMESim.h"

int main() {
	std::vector<AdaptationTask> tasks = std::vector<AdaptationTask>();
	GIMMESim sim = GIMMESim(
		100, 50, 30,
		23, 1, 30,
		100, 5, 30,
		2, 5,
		5,
		tasks,
		tasks,
		tasks);
	sim.simulate();
}