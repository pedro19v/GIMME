#include "Headers\User\UserParameter.h"

UserParameter::UserParameter(float minScaleValue, float maxScaleValue, std::string  name, float value)
{
	this->minScaleValue = minScaleValue;
	this->maxScaleValue = maxScaleValue;

	this->name = name;
	this->value = value;

}

UserParameter::UserParameter(float minScaleValue, float maxScaleValue, std::string name)
{
	this->minScaleValue = minScaleValue;
	this->maxScaleValue = maxScaleValue;

	this->name = name;
	this->value = 0;

}

UserParameter::UserParameter()
{
	this->minScaleValue = 0;
	this->maxScaleValue = 0;

	this->name = "unnamed parameter";
	this->value = 0;
}


std::vector<float> UserParameter::getScale()
{
	std::vector<float> scale = std::vector<float>(2);
	scale[0] = minScaleValue;
	scale[0] = maxScaleValue;
	return scale;
}
std::string UserParameter::getName()
{
	return this->name;
}
float UserParameter::getValue()
{
	return this->value;
}

void UserParameter::setName(std::string name)
{
	this->name = name;
}
void UserParameter::setValue(float value)
{
	this->value = value;
}

void UserParameter::setScale(float minValue, float maxValue)
{
	this->minScaleValue = minValue;
	this->maxScaleValue = maxValue;
}





