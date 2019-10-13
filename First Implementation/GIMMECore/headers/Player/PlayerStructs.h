#include "..//AuxStructs//InteractionsProfile.h"

//auxiliary structures: Player
struct PlayerCharacteristics {
	double ability; // score percentage
	double engagement; // on vs off task percentage
};
struct PlayerState {
	InteractionsProfile profile;
	PlayerCharacteristics characteristics;
	double dist;
};
