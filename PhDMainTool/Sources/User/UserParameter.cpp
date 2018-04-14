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

}

UserParameter::UserParameter(float minScaleValue, float maxScaleValue)
{
	this->minScaleValue = minScaleValue;
	this->maxScaleValue = maxScaleValue;
}


std::vector<float> UserParameter::getScale()
{
	return std::vector<float>(minScaleValue, maxScaleValue);
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





