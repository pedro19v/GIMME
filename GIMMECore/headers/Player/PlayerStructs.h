#include "../AuxStructs/InteractionsProfile.h"

//auxiliary structures: Player
struct PlayerCharacteristics {
	double engagement; // on vs off task percentage
	double ability; // score percentage
};
struct PlayerState {
	InteractionsProfile profile;
	PlayerCharacteristics characteristics;
	double dist;
};
