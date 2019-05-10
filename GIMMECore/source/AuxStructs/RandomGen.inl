#include "..\AuxStructs\RandomGen.h"


//has to be put here so that the compiler links the code directly on the header. If this is not done, the linker will not manage to find the definitions of templated functions
template <class c>
void RandomGen::randShuffle(std::vector<c>& vector) {
	static std::default_random_engine randomGenerator(defaultRandomSeed);
	shuffle(vector.begin(), vector.end(), randomGenerator);
}