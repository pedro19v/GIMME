#pragma once

#include<vector>
#include<string>

class UserParameter
{
private:
	float minScaleValue;
	float maxScaleValue;

	std::string name;
	float value;
public:
	UserParameter(float minScaleValue, float maxScaleValue, std::string name, float value);
	UserParameter(float minScaleValue, float maxScaleValue, std::string name);
	UserParameter(float minScaleValue, float maxScaleValue);

	std::vector<float> getScale();

	std::string getName();
	float getValue();

	void setName(std::string name);
	void setValue(float value);
	void setScale(float minValue, float maxValue);

};