//#pragma once
//
//#include "Json.h"
//
//
//
//
//template<typename T> T& Json::asAny(Value&);
//template<typename T> const T& Json::asAny(const Value&);
//
//template<>
//int& Json::asAny<int>(Value& value) {
//	return value.data.number;
//}
//
//template<>
//const int& Json::asAny<int>(const Value& value) {
//	return value.data.number;
//}
//
//template<>
//const std::string& Json::asAny<std::string>(const Value& value) {
//	return value.data.string;
//}
//
//template<>
//std::string& Json::asAny<std::string>(Value& value) {
//	return value.data.string;
//}
//
//
//
//
//
