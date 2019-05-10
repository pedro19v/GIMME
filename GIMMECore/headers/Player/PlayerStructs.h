//auxiliary structures: Player
struct InteractionsProfile {
public:
	double K_i;
	double K_cp;
	double K_cl;

	InteractionsProfile(double K_i, double K_cp, double K_cl)
	{
		this->K_i = K_i;
		this->K_cp = K_cp;
		this->K_cl = K_cl;
	}

	InteractionsProfile()
	{
		this->K_i = 0.0;
		this->K_cp = 0.0;
		this->K_cl = 0.0;
	}

	double normalizedDistanceBetween(InteractionsProfile profile2)
	{
		InteractionsProfile profile1 = *this;
		InteractionsProfile cost = { 0,0,0 };
		//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = std::abs(profile1.K_cl - profile2.K_cl);
		cost.K_cp = std::abs(profile1.K_cp - profile2.K_cp);
		cost.K_i = std::abs(profile1.K_i - profile2.K_i);

		double totalDiff = cost.K_cl + cost.K_cp + cost.K_i;

		cost.K_cl /= totalDiff;
		cost.K_cp /= totalDiff;
		cost.K_i /= totalDiff;

		cost.K_cl = std::pow(cost.K_cl, 2);
		cost.K_cp = std::pow(cost.K_cl, 2);
		cost.K_i = std::pow(cost.K_cl, 2);

		return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
	}

	double distanceBetween(InteractionsProfile profile2)
	{
		InteractionsProfile profile1 = *this;
		InteractionsProfile cost = { 0,0,0 };
		//normalizar cada uma das dims X/X+Y+Z; Y/X+Y+Z, Z/X+Y+Z
		cost.K_cl = std::abs(profile1.K_cl - profile2.K_cl);
		cost.K_cp = std::abs(profile1.K_cp - profile2.K_cp);
		cost.K_i = std::abs(profile1.K_i - profile2.K_i);


		cost.K_cl = std::pow(cost.K_cl, 2);
		cost.K_cp = std::pow(cost.K_cl, 2);
		cost.K_i = std::pow(cost.K_cl, 2);

		return sqrt(cost.K_cl + cost.K_cp + cost.K_i);
	}

};
struct PlayerCharacteristics {
	double engagement; // on vs off task percentage
	double ability; // score percentage
};
struct PlayerState {
	InteractionsProfile profile;
	PlayerCharacteristics characteristics;
	double dist;
};
