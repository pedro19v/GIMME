struct LearningState {
	InteractionsProfile currProfile;
	double engagement; // on vs off task percentage
	double ability; // score percentage

	double dist;
};


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

struct AdaptationGroup {
private:
	Student::LearningState avgLearningState;
	InteractionsProfile avgPreferences;
	InteractionsProfile learningProfile;
	std::vector<Student*> students;
public:


	void addStudent(Student* student) {

		students.push_back(student);
		int studentsSize = students.size();


		//recalculate averages
		avgLearningState = Student::LearningState();
		avgPreferences.K_cl = 0;
		avgPreferences.K_cp = 0;
		avgPreferences.K_i = 0;

		for (int i = 0; i < studentsSize; i++) {
			Student* currStudent = students[i];
			InteractionsProfile currStudentPreference = currStudent->getInherentPreference();
			avgLearningState.engagement += currStudent->getEngagement() / studentsSize;
			avgLearningState.ability += currStudent->getAbility() / studentsSize;
			avgPreferences.K_cl += currStudentPreference.K_cl / studentsSize;
			avgPreferences.K_cp += currStudentPreference.K_cp / studentsSize;
			avgPreferences.K_i += currStudentPreference.K_i / studentsSize;
		}

	}
	std::vector<Student*> getStudents() {
		return this->students;
	}
	void setLearningProfile(InteractionsProfile learningProfile) {
		this->learningProfile = learningProfile;
	}

	InteractionsProfile getInteractionsProfile() {
		return this->learningProfile;
	}
	Student::LearningState getAvgLearningState() {
		return this->avgLearningState;
	}
	InteractionsProfile getAvgPreferences() {
		return this->avgPreferences;
	}
};
struct AdaptationConfiguration {
public:
	std::vector<AdaptationGroup> groups;
};
enum AdaptationTaskType {
	COLLABORATION = 0,
	COMPETITION = 1,
	SELF_INTERACTION = 2
};
struct AdaptationTask {
private:
	/*struct WayToSortTaskInstances {
		bool operator()(const AdaptationTask& i, const AdaptationTask& j) { return i.minRequiredAbility < j.minRequiredAbility; }
	};*/
public:
	AdaptationTaskType type;
	std::string description;
	float minRequiredAbility;
	std::vector<AdaptationTask> taskInstances; //maintained in order

	AdaptationTask(AdaptationTaskType type, std::string description, float minRequiredAbility, std::vector<AdaptationTask> taskInstances) {
		this->type = type;
		this->description = description;
		this->minRequiredAbility = minRequiredAbility;

		//std::sort(taskInstances.begin(), taskInstances.end(), WayToSortTaskInstances());
		this->taskInstances = taskInstances;
	}
	AdaptationTask(AdaptationTaskType type, std::string description, std::vector<AdaptationTask> taskInstances) : AdaptationTask(type, description, 0, taskInstances) {}
	AdaptationTask(AdaptationTaskType type, std::string description, float minRequiredAbility) : AdaptationTask(type, description, minRequiredAbility, std::vector<AdaptationTask>()) {}
};