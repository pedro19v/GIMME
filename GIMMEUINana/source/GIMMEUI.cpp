#include "../headers/GIMMEUI.h"

int main()
{
	std::vector<AdaptationTask> possibleCollaborativeTasks = std::vector<AdaptationTask>();
	std::vector<AdaptationTask> possibleCompetitiveTasks = std::vector<AdaptationTask>();
	std::vector<AdaptationTask> possibleIndividualTasks = std::vector<AdaptationTask>();

	possibleCollaborativeTasks.clear();
	std::vector<AdaptationTask> taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1Inst5", 0.9f));
	AdaptationTask task1 = AdaptationTask(AdaptationTaskType::COLLABORATION, "collab1", taskInstances);
	possibleCollaborativeTasks.push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2Inst5", 0.9f));
	AdaptationTask task2 = AdaptationTask(AdaptationTaskType::COLLABORATION, "collab2", taskInstances);
	possibleCollaborativeTasks.push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3Inst5", 0.9f));
	AdaptationTask task3 = AdaptationTask(AdaptationTaskType::COLLABORATION, "collab3", taskInstances);
	possibleCollaborativeTasks.push_back(task3);

	possibleCompetitiveTasks.clear();
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp1Inst5", 0.9f));
	task1 = AdaptationTask(AdaptationTaskType::COMPETITION, "comp1", taskInstances);
	possibleCompetitiveTasks.push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp2Inst5", 0.9f));
	task2 = AdaptationTask(AdaptationTaskType::COMPETITION, "comp2", taskInstances);
	possibleCompetitiveTasks.push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::COMPETITION, "comp3Inst5", 0.9f));
	task3 = AdaptationTask(AdaptationTaskType::COMPETITION, "comp3", taskInstances);
	possibleCompetitiveTasks.push_back(task3);

	possibleIndividualTasks.clear();
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1Inst5", 0.9f));
	task1 = AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self1", taskInstances);
	possibleIndividualTasks.push_back(task1);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2Inst5", 0.9f));
	task2 = AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self2", taskInstances);
	possibleIndividualTasks.push_back(task2);
	taskInstances = std::vector<AdaptationTask>();
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst1", 0.1f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst2", 0.3f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst3", 0.5f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst4", 0.7f));
	taskInstances.push_back(AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3Inst5", 0.9f));
	task3 = AdaptationTask(AdaptationTaskType::SELF_INTERACTION, "self3", taskInstances);
	possibleIndividualTasks.push_back(task3);
	
	
	int numStudentsInClass = 23;

	Utilities* utilities = new Utilities();
	utilities->resetRandoms();
	
	//generate all of the students models
	std::vector<Student*> students = std::vector<Student*>();
	/*for (int i = 0; i < numStudentsInClass; i++) {
		students.push_back(new Student(i, "a", 1, 1, 1, utilities));
	}*/
	Adaptation adapt;
	
	//getchar();


	nana::form fm;
	nana::textbox outputLabel{ fm };
	//outputLabel.format(true);
	//outputLabel.bgcolor(nana::color(256, 256, 256, 1.0f));
	nana::button btn{ fm };
	btn.caption("iterate");
	btn.events().click([&fm, &outputLabel, &adapt] {
		std::vector<std::pair<AdaptationGroup, AdaptationMechanic>> groupMechanicPairs = adapt.iterate();
		groupMechanicPairs = adapt.iterate();
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
			
			mechanicsOutput += "Profile: <K_cl: "+ std::to_string(currProfile.K_cl) + " , K_cp: " + std::to_string(currProfile.K_cp) + " , K_i: " + std::to_string(currProfile.K_i) + ">";
			
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
	fm.div("vert <><<><width=80% text><>><><weight=24<><button><>><>");
	fm["text"] << outputLabel;
	fm["button"] << btn;
	fm.collocate();

	

	//Define a form object, class form will create a window
	//when a form instance is created.
	//The new window default visibility is false.
	nana::form initFm;
	nana::textbox studentIDLabel{ initFm };
	nana::textbox studentNameLabel{ initFm };
	nana::button addStudentButton{ initFm };
	addStudentButton.caption("Add Student");
	addStudentButton.events().click([&initFm, &studentIDLabel, &studentNameLabel, &students, &utilities] {
		students.push_back(new Student(std::stoi(std::string(studentIDLabel.caption())), std::string(studentNameLabel.caption()), 1, 1, 1, utilities));
	});
	nana::button startAdaptationButton{ initFm };
	startAdaptationButton.caption("Start Adaptation");
	startAdaptationButton.events().click([&initFm, &fm, &adapt, &students, &utilities, &possibleCollaborativeTasks, &possibleCompetitiveTasks, &possibleIndividualTasks] {
		adapt = Adaptation(
			"test",
			students,
			100,
			2, 5,
			5,
			utilities,
			5, possibleCollaborativeTasks, possibleCompetitiveTasks, possibleIndividualTasks);

		//Expose the form.
		fm.restore();
		fm.show();
	});

	//manage layout
	initFm.div("vert <><<><width=80% text><>><<><width=80% text2><>> <weight=24<><button><>><weight=24<><button2><>><>");
	initFm["text"] << studentIDLabel;
	initFm["text2"] << studentNameLabel;
	initFm["button"] << addStudentButton;
	initFm["button2"] << startAdaptationButton;
	initFm.collocate();
	initFm.show();
	

	//Pass the control of the application to Nana's event
	//service. It blocks the execution for dispatching user
	//input until the form is closed.
	nana::exec();

}
