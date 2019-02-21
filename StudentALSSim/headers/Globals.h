#pragma once
#include <vector>
#include "Student.h"

struct AdaptationTask; //forward declaration

class Globals {
public:
	static std::vector<Student*>  students;

	static std::vector<AdaptationTask> possibleCollaborativeTasks;
	static std::vector<AdaptationTask> possibleCompetitiveTasks;
	static std::vector<AdaptationTask> possibleIndividualTasks;
};