#include "../headers/GIMMEUI.h"

class UpdatePlayerStatesForm : public nana::form {

private:
	nana::label studentDescriptionLabel;
	nana::label studentAbilityLabel;
	nana::label studentEngagementLabel;

	nana::textbox studentAbilityInput;
	nana::textbox studentEngagementInput;

	nana::button updateStudentsButton;
public:

	UpdatePlayerStatesForm()
	{}

	void create(std::vector<Student*>* students){
		this->div("vert <studentDescriptionLabels> <<stateLabels><stateInputs>> <buttons>");

		std::vector<nana::textbox> studentAbilityInputs = std::vector<nana::textbox>();
		std::vector<nana::textbox> studentEngagementInputs = std::vector<nana::textbox>();

		for (int i = 0; i < students->size(); i++) {
			Student* currStudent = (*students)[i];

			studentDescriptionLabel.create(*this);
			studentDescriptionLabel.caption("Student Id: " + std::to_string(currStudent->getId()) + ", name: " + currStudent->getName());

			studentAbilityLabel.create(*this);
			studentAbilityLabel.caption("Ability: ");
			studentAbilityInput.create(*this);

			studentEngagementLabel.create(*this);
			studentEngagementLabel.caption("Engagement: ");
			studentEngagementInput.create(*this);

			/*studentAbilityInputs.push_back(studentAbilityInput);
			studentEngagementInputs.push_back(studentEngagementInput);*/

			(*this)["studentDescriptionLabels"] << studentDescriptionLabel;
			(*this)["stateLabels"] << studentAbilityLabel;
			(*this)["stateLabels"] << studentEngagementLabel;
			(*this)["stateInputs"] << studentAbilityInput;
			(*this)["stateInputs"] << studentEngagementInput;
		}

		updateStudentsButton.create(*this);
		updateStudentsButton.caption("Update Students Characteristics");
		updateStudentsButton.events().click([this] {
			/*for (int i = 0; i < students->size(); i++) {
				Student* currStudent = (*students)[i];
				currStudent->setCharacteristics(PlayerCharacteristics{ std::stod(studentAbilityInputs[i].caption()),std::stod(studentEngagementInputs[i].caption()) });
			}*/
		});

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
		outputLabel.create(*this);

		iterateButton.create(*this);
		iterateButton.caption("iterate");
		iterateButton.events().click([this, adapt] {
			std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> groupMechanicPairs = adapt->iterate();
			groupMechanicPairs = adapt->iterate();
			int mechanicsSize = (int)groupMechanicPairs.size();
			std::string mechanicsOutput = "";

			for (int j = 0; j < mechanicsSize; j++) {
				std::vector<Student*> currGroup = groupMechanicPairs[j].first.getStudents();
				std::vector<AdaptationTask> currMechanic = groupMechanicPairs[j].second.tasks;
				InteractionsProfile currProfile = groupMechanicPairs[j].second.profile;

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

public:

	PlayerSetupForm()
	{}

	void create(AdaptationForm* adaptationForm, std::vector<Student*>* students, Adaptation* adapt, Utilities* utilities, std::vector<AdaptationTask>* possibleCollaborativeTasks, std::vector<AdaptationTask>* possibleCompetitiveTasks, std::vector<AdaptationTask>* possibleIndividualTasks){
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
		nana::form warning;
		nana::label label{ warning };
		label.caption("Student Id must be a positive integer!");
		warning.div("vert <label>");
		warning["label"] << label;

		warning.collocate();


		addStudentButton.events().click([this,&warning, &students, &utilities] {
			if (!isNumber(studentIDInput.caption())) {
				warning.show();
				return;
			}
			Student* newStudent = new Student(std::stoi(studentIDInput.caption()), std::string(studentNameInput.caption()), 1, 1, 1, utilities);
			students->push_back(newStudent);
			studentIDInput.reset();
			studentNameInput.reset();
			currStudentsDisplay.append(newStudent->getName() + "|" + std::to_string(newStudent->getId()) + "\n", true);
		});

		removeStudentButton.create(*this);
		removeStudentButton.caption("Remove Student");
		removeStudentButton.events().click([this, &students, &utilities] {
			currStudentsDisplay.reset();
			int studentsInitialSize = students->size();
			std::vector<int> oldStudentsIndexes;
			for (int i = 0; i < studentsInitialSize; i++) {
				Student* currStudent = (*students)[i];
				if (currStudent->getId() == std::stoi(studentIDInput.caption())) {
					oldStudentsIndexes.push_back(i);
					continue;
				}
				currStudentsDisplay.append(currStudent->getName() + "|" + std::to_string(currStudent->getId()) + "\n", true);
			}

			for (int i = oldStudentsIndexes.size(); i > 0; i--) {
				students->erase(students->begin() + oldStudentsIndexes[i]);
			}
		});

		startAdaptationButton.create(*this);
		startAdaptationButton.caption("Start Adaptation");
		startAdaptationButton.events().click([this, adaptationForm, &students, &adapt, &utilities, &possibleCollaborativeTasks, &possibleCompetitiveTasks, &possibleIndividualTasks] {
			if (adapt != NULL) {
				delete adapt;
			}
			adapt = new Adaptation(
				"test",
				students,
				100,
				2, 5,
				5,
				utilities,
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






int main()
{
	std::vector<AdaptationTask>* possibleCollaborativeTasks = new std::vector<AdaptationTask>();
	std::vector<AdaptationTask>* possibleCompetitiveTasks = new std::vector<AdaptationTask>();
	std::vector<AdaptationTask>* possibleIndividualTasks = new std::vector<AdaptationTask>();

	possibleCollaborativeTasks->clear();
	std::vector<AdaptationTask> taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst5", 0.9f));
	AdaptationTask task1 = AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1", taskInstances);
	possibleCollaborativeTasks->push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst5", 0.9f));
	AdaptationTask task2 = AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2", taskInstances);
	possibleCollaborativeTasks->push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst5", 0.9f));
	AdaptationTask task3 = AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3", taskInstances);
	possibleCollaborativeTasks->push_back(task3);

	possibleCompetitiveTasks->clear();
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst5", 0.9f));
	task1 = AdaptationTask(AdaptationTaskType::COMPETITION, "comp1", taskInstances);
	possibleCompetitiveTasks->push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst5", 0.9f));
	task2 = AdaptationTask(AdaptationTaskType::COMPETITION, "comp2", taskInstances);
	possibleCompetitiveTasks->push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst5", 0.9f));
	task3 = AdaptationTask(AdaptationTaskType::COMPETITION, "comp3", taskInstances);
	possibleCompetitiveTasks->push_back(task3);

	possibleIndividualTasks->clear();
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst5", 0.9f));
	task1 = AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1", taskInstances);
	possibleIndividualTasks->push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst5", 0.9f));
	task2 = AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2", taskInstances);
	possibleIndividualTasks->push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst5", 0.9f));
	task3 = AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3", taskInstances);
	possibleIndividualTasks->push_back(task3);
	
	
	int numStudentsInClass = 23;

	Utilities* utilities = new Utilities();
	utilities->resetRandoms();
	
	//generate all of the students models
	std::vector<Student*>* students = new std::vector<Student*>();
	/*for (int i = 0; i < numStudentsInClass; i++) {
		students->push_back(new Student(i, "a", 1, 1, 1, utilities));
	}*/
	Adaptation* adapt = NULL;
	
	//getchar();

	AdaptationForm adaptationForm;


	PlayerSetupForm playerSetupForm;
	playerSetupForm.create(&adaptationForm, students, adapt, utilities, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks);
	playerSetupForm.show();


	UpdatePlayerStatesForm updateForm;
	updateForm.create(students);
	updateForm.show();

	//nana::form& playerSetupForm = nana::form_loader<nana::form, true>()();
	//buildPlayerSetupForm(playerSetupForm, af, students, adapt, utilities, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks);
	//playerSetupForm.show();

	//nana::form& setPlayerStateForm = nana::form_loader<nana::form, true>()();
	//setPlayerStateForm.div("vert <studentDescriptionLabels> <<stateLabels><stateInputs>> <buttons>");

	//std::vector<nana::textbox> studentAbilityInputs = std::vector<nana::textbox>();
	//std::vector<nana::textbox> studentEngagementInputs = std::vector<nana::textbox>();

	//for (int i = 0; i < students->size(); i++) {
	//	Student* currStudent = (*students)[i];

	//	nana::label studentDescriptionLabel{ setPlayerStateForm };
	//	studentDescriptionLabel.caption("Student Id: " + std::to_string(currStudent->getId()) + ", name: " + currStudent->getName());

	//	nana::label studentAbilityLabel{ setPlayerStateForm };
	//	studentAbilityLabel.caption("Ability: ");
	//	nana::textbox studentAbilityInput{ setPlayerStateForm };

	//	nana::label studentEngagementLabel{ setPlayerStateForm };
	//	studentEngagementLabel.caption("Engagement: ");
	//	nana::textbox studentEngagementInput{ setPlayerStateForm };

	//	/*studentAbilityInputs.push_back(studentAbilityInput);
	//	studentEngagementInputs.push_back(studentEngagementInput);*/

	//	setPlayerStateForm["studentDescriptionLabels"] << studentDescriptionLabel;
	//	setPlayerStateForm["stateLabels"] << studentAbilityLabel;
	//	setPlayerStateForm["stateLabels"] << studentEngagementLabel;
	//	setPlayerStateForm["stateInputs"] << studentAbilityInput;
	//	setPlayerStateForm["stateInputs"] << studentEngagementInput;
	//}

	//nana::button updateStudentsButton{ setPlayerStateForm };
	//updateStudentsButton.caption("Update Students Characteristics");
	//updateStudentsButton.events().click([&students, &studentAbilityInputs, &studentEngagementInputs] {
	//	for (int i = 0; i < students->size(); i++) {
	//		Student* currStudent = (*students)[i];
	//		currStudent->setCharacteristics(PlayerCharacteristics{ std::stod(studentAbilityInputs[i].caption()),std::stod(studentEngagementInputs[i].caption()) });
	//	}
	//});
	//setPlayerStateForm["buttons"] << updateStudentsButton;

	//setPlayerStateForm.collocate();
	//setPlayerStateForm.show();

	
	//Pass the control of the application to Nana's event
	//service. It blocks the execution for dispatching user
	//input until the form is closed.
	nana::exec();

}


