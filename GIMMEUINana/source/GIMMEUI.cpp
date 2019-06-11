#include "../headers/GIMMEUI.h"


class UpdateSinglePlayerStateForm : public nana::form {

private:
	nana::label abilityLabel;
	nana::label engagementLabel;

	nana::inputbox::real studentAbilityInput {"Ability(%)", 100, 1, 300, 1 };
	nana::inputbox::real studentEngagementInput{ "Engagement(%)", 100, 1, 300, 1 };

	nana::button updateStudentsButton;
public:

	UpdateSinglePlayerStateForm()
	{
		
	}
	void updateTarget(Player* student) {
		//update event to match new target
		updateStudentsButton.events().click([this, student] {
			student->setCharacteristics(PlayerCharacteristics{ 
				studentAbilityInput.value(),
				studentEngagementInput.value()
			});
			this->hide();
		});
	}

	void create() {
		this->div("vert <stateLabels> <stateInputs> <button>");

		abilityLabel.create(*this);
		abilityLabel.caption("Ability: ");

		engagementLabel.create(*this);
		engagementLabel.caption("Engagement: ");

		/*studentAbilityInput.create(*this);
		studentEngagementInput.create(*this);*/

		(*this)["stateLabels"] << abilityLabel;
		(*this)["stateLabels"] << engagementLabel;
		/*(*this)["stateInputs"] << studentAbilityInput;
		(*this)["stateInputs"] << studentEngagementInput;*/

		updateStudentsButton.create(*this);
		updateStudentsButton.caption("Update Student Characteristics");
		(*this)["button"] << updateStudentsButton;

		(*this).collocate();
	}



};

class UpdatePlayerStatesForm : public nana::form {

private:
	nana::button* studentDescriptionLabels;

	nana::textbox* studentAbilityInputs;
	nana::textbox* studentEngagementInputs;

	UpdateSinglePlayerStateForm popupForm;
	
	
public:

	UpdatePlayerStatesForm()
	{}

	void create(std::vector<Player*>* students){
		studentAbilityInputs = new nana::textbox[students->size()];
		studentEngagementInputs = new nana::textbox[students->size()];
		studentDescriptionLabels = new nana::button[students->size()];

		this->div("horizontal <studentDescriptionLabels>");

		//studentDescriptionLabels.create(*this);
		//auto node = studentDescriptionLabels.insert("root", "Students"); // "Student Id: " + std::to_string(currStudent->getId()) + ", name: " + currStudent->getName());
		
		//prevent from unloading on close
		popupForm.events().unload([this](const nana::arg_unload& arg) {
			popupForm.hide();
			arg.cancel = true;
		});
		(*this).events().unload([](const nana::arg_unload& arg) {
			arg.cancel = true;
		});

		popupForm.create();
		popupForm.updateTarget((*students)[0]);

		for (int i = 0; i < students->size(); i++) {
			Player* currStudent = (*students)[i];

			studentDescriptionLabels[i].create(*this);
			studentDescriptionLabels[i].caption("Student Id: " + std::to_string(currStudent->getId()) + ", name: " + currStudent->getName());

			auto currButton = &studentDescriptionLabels[i];
			//studentDescriptionLabels[i].bgcolor(nana::colors::aquamarine);
			currButton->events().click([this, currStudent, currButton] {
				currButton->bgcolor(nana::colors::green);
				popupForm.updateTarget(currStudent);
				popupForm.show();
			});
			
			(*this)["studentDescriptionLabels"] << studentDescriptionLabels[i];
		}

		
		this->collocate();
	}

	~UpdatePlayerStatesForm()
	{
		delete[] studentAbilityInputs;
		delete[] studentEngagementInputs;
	}

};





class AdaptationForm : public nana::form {

private:
	nana::textbox outputLabel;
	nana::button iterateButton;

public:
	AdaptationForm()
	{}

	void create(Adaptation* adapt){
		
		(*this).events().unload([](const nana::arg_unload& arg) {
			arg.cancel = true;
		});
		
		outputLabel.create(*this);

		iterateButton.create(*this);
		iterateButton.caption("iterate");
		iterateButton.events().click([this, adapt] {
			AdaptationConfiguration config = adapt->iterate();
			std::vector<AdaptationGroup> groups = config.groups;
			int mechanicsSize = (int) groups.size();
			std::string mechanicsOutput = "";

			for (int j = 0; j < mechanicsSize; j++) {
				std::vector<Player*> currGroup = groups[j].players;
				std::vector<AdaptationTask> currMechanic = groups[j].tailoredMechanic.tasks;
				InteractionsProfile currProfile = groups[j].tailoredMechanic.profile;

				mechanicsOutput += "promote on students:\n";
				for (int k = 0; k < currGroup.size(); k++) {
					mechanicsOutput += "Number: " + std::to_string(currGroup[k]->getId()) + ", Name: " + currGroup[k]->getName() + "\n";
				}

				mechanicsOutput += "Profile: <K_cl: " + std::to_string(currProfile.K_cl) + " , K_cp: " + std::to_string(currProfile.K_cp) + " , K_i: " + std::to_string(currProfile.K_i) + ">";

				mechanicsOutput += ", the following tasks:\n";
				for (int k = 0; k < currMechanic.size(); k++) {
					mechanicsOutput += currMechanic[k].description + "\n";
				}
				mechanicsOutput += "-- -- -- -- -- -- -- -- -- -- -- -- --\n";
			}
			mechanicsOutput += "----------------------End of Iteration--------------------\n";
			outputLabel.append(mechanicsOutput, true);
		});

		//manage layout
		this->div("vert <><<><width=80% text><>><><weight=24<><button><>><>");
		(*this)["text"] << outputLabel;
		(*this)["button"] << iterateButton;
		this->collocate();
	}
};




class PlayerSetupForm : public nana::form {

private:
	nana::textbox currStudentsDisplay;
	
	nana::label studentIDLabel;
	nana::textbox studentIDInput;

	nana::label studentNameLabel;
	nana::textbox studentNameInput;

	nana::button addStudentButton;
	nana::button removeStudentButton;
	nana::button startAdaptationButton;

	nana::form warning;

public:

	PlayerSetupForm()
	{}

	void create(AdaptationForm* adaptationForm, std::vector<Player*>* players, Adaptation* adapt, RandomGen* randomGen, std::vector<AdaptationTask>* possibleCollaborativeTasks, std::vector<AdaptationTask>* possibleCompetitiveTasks, std::vector<AdaptationTask>* possibleIndividualTasks){
		(*this).events().unload([](const nana::arg_unload& arg) {
			arg.cancel = true;
		});
		
		currStudentsDisplay.create(*this);
		currStudentsDisplay.append("------------ [Registered Players] -------------\n", true);
		currStudentsDisplay.append("Name: | ID: \n", true);

		studentIDLabel.create(*this);
		studentIDLabel.caption("New Student Id: ");
		studentIDInput.create(*this);
		studentIDInput.multi_lines(false);

		studentNameLabel.create(*this);
		studentNameLabel.caption("New Student Name: ");
		studentNameInput.create(*this);
		studentNameInput.multi_lines(false);

		addStudentButton.create(*this);
		addStudentButton.caption("Add Student");


		//create warning popups
		nana::label label;
		label.create(warning);
		label.caption("Student Id must be a positive integer!");
		warning.div("vert <label>");
		warning["label"] << label;
		warning.collocate();


		addStudentButton.events().click([this, &players, &randomGen] {
			if (!isNumber(studentIDInput.caption())) {
				warning.show();
				return;
			}
			Player* newStudent = new Player(std::stoi(studentIDInput.caption()), std::string(studentNameInput.caption()), 1, 1, 1, randomGen);
			players->push_back(newStudent);
			studentIDInput.reset();
			studentNameInput.reset();
			currStudentsDisplay.append(newStudent->getName() + "|" + std::to_string(newStudent->getId()) + "\n", true);
		});

		removeStudentButton.create(*this);
		removeStudentButton.caption("Remove Student");
		removeStudentButton.events().click([this, &players, &randomGen] {
			if (!isNumber(studentIDInput.caption())) {
				warning.show();
				return;
			}

			currStudentsDisplay.reset();
			int studentsInitialSize = players->size();
			std::vector<int> oldStudentsIndexes;
			for (int i = 0; i < studentsInitialSize; i++) {
				Player* currStudent = (*players)[i];
				if (currStudent->getId() == std::stoi(studentIDInput.caption())) {
					oldStudentsIndexes.push_back(i);
					continue;
				}
				currStudentsDisplay.append(currStudent->getName() + "|" + std::to_string(currStudent->getId()) + "\n", true);
			}

			for (int i = oldStudentsIndexes.size()-1; i > -1; i--) {
				players->erase(players->begin() + oldStudentsIndexes[i]);
			}
		});


		startAdaptationButton.create(*this);
		startAdaptationButton.caption("Start Adaptation");
		startAdaptationButton.events().click([this, adaptationForm, &players, &adapt, &randomGen, &possibleCollaborativeTasks, &possibleCompetitiveTasks, &possibleIndividualTasks] {
			if (adapt != NULL) {
				delete adapt;
			}
			adapt = new Adaptation(
				"test",
				players,
				100,
				2, 5,
				new KNNRegression(5),
				new RandomConfigsGen(),
				new FundamentedFitness(),
				randomGen,
				5, *possibleCollaborativeTasks, *possibleCompetitiveTasks, *possibleIndividualTasks);

			adaptationForm->create(adapt);
			adaptationForm->show();
		});
		this->div("vert <height=70% currStudentsDisplay> <height=10% studentIDElements> <height=10% studentNameElements> <height=10% buttons>");
		(*this)["currStudentsDisplay"] << currStudentsDisplay;
		(*this)["studentIDElements"] << studentIDLabel;
		(*this)["studentIDElements"] << studentIDInput;
		(*this)["studentNameElements"] << studentNameLabel;
		(*this)["studentNameElements"] << studentNameInput;
		(*this)["buttons"] << addStudentButton;
		(*this)["buttons"] << removeStudentButton;
		(*this)["buttons"] << startAdaptationButton;

		this->collocate();
	}
	bool isNumber(const std::string& s)
	{
		std::string::const_iterator it = s.begin();
		while (it != s.end() && std::isdigit(*it)) ++it;
		return !s.empty() && it == s.end();
	}
};

//void onExit() {
//	if (this->regAlg != NULL) {
//		delete regAlg;
//	}
//	if (this->fitAlg != NULL) {
//		delete fitAlg;
//	}
//	if (this->configsGenAlg != NULL) {
//		delete configsGenAlg;
//	}
//	if (this->randomGen != NULL) {
//		delete randomGen;
//	}
//}





int main()
{
	std::vector<AdaptationTask>* possibleCollaborativeTasks = new std::vector<AdaptationTask>();
	std::vector<AdaptationTask>* possibleCompetitiveTasks = new std::vector<AdaptationTask>();
	std::vector<AdaptationTask>* possibleIndividualTasks = new std::vector<AdaptationTask>();

	possibleCollaborativeTasks->clear();
	std::vector<AdaptationTask> taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab1Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab1Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab1Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab1Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab1Inst5", 0.9f });
	AdaptationTask task1 = AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab1", 0.1f, taskInstances };
	possibleCollaborativeTasks->push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab2Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab2Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab2Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab2Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab2Inst5", 0.9f });
	AdaptationTask task2 = AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab2", 0.1f, taskInstances };
	possibleCollaborativeTasks->push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab3Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab3Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab3Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab3Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab3Inst5", 0.9f });
	AdaptationTask task3 = AdaptationTask{ AdaptationTaskType::COLLABORATION, "collab3", 0.1f, taskInstances };
	possibleCollaborativeTasks->push_back(task3);

	possibleCompetitiveTasks->clear();
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp1Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp1Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp1Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp1Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp1Inst5", 0.9f });
	task1 = AdaptationTask{ AdaptationTaskType::COMPETITION, "comp1", 0.1f, taskInstances };
	possibleCompetitiveTasks->push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp2Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp2Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp2Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp2Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp2Inst5", 0.9f });
	task2 = AdaptationTask{ AdaptationTaskType::COMPETITION, "comp2", 0.1f, taskInstances };
	possibleCompetitiveTasks->push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp3Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp3Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp3Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp3Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::COMPETITION, "comp3Inst5", 0.9f });
	task3 = AdaptationTask{ AdaptationTaskType::COMPETITION, "comp3", 0.1f, taskInstances };
	possibleCompetitiveTasks->push_back(task3);

	possibleIndividualTasks->clear();
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self1Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self1Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self1Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self1Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self1Inst5", 0.9f });
	task1 = AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self1", 0.1f, taskInstances };
	possibleIndividualTasks->push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self2Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self2Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self2Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self2Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self2Inst5", 0.9f });
	task2 = AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self2", 0.1f, taskInstances };
	possibleIndividualTasks->push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self3Inst1", 0.1f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self3Inst2", 0.3f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self3Inst3", 0.5f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self3Inst4", 0.7f });
	taskInstances.push_back(AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self3Inst5", 0.9f });
	task3 = AdaptationTask{ AdaptationTaskType::SELF_INTERACTION, "self3", 0.1f, taskInstances };
	possibleIndividualTasks->push_back(task3);
	
	
	int numStudentsInClass = 23;

	RandomGen* utilities = new RandomGen();
	utilities->resetRandoms();
	
	//generate all of the students models
	std::vector<Player*>* students = new std::vector<Player*>();
	for (int i = 0; i < numStudentsInClass; i++) {
		students->push_back(new Player(i, "a", 1, 1, 1, utilities));
	}
	Adaptation* adapt = NULL;
	
	//getchar();

	AdaptationForm adaptationForm;


	PlayerSetupForm playerSetupForm;
	playerSetupForm.create(&adaptationForm, students, adapt, utilities, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks);
	playerSetupForm.show();


	UpdatePlayerStatesForm updateForm;
	updateForm.create(students);
	updateForm.show();


	
	nana::exec();

}


