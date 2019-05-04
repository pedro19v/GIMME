#pragma once
#include "Adaptation.h"

class IConfigsGenAlg
{
public:
	AdaptationConfiguration organize(std::vector<Student*> students) {
	};
};

class RandomGen : public IConfigsGenAlg {
public:
	AdaptationConfiguration organize(std::vector<Student*> students);
};

class EvolutionaryGen : public IConfigsGenAlg {
public:
	AdaptationConfiguration organize(std::vector<Student*> students);
};
