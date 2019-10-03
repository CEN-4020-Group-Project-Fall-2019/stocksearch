#ifndef OPTIONDATA_H
#define OPTIONDATA_H

#include "CSVReader.h"
class OptionData : public CSVReader{
public:
	OptionData(char* fn);
	void tokenize();
	bool* comparePrices(double* optionPrices);
// private:
	vector<char> call;
	vector<double> exp;
	vector<double> strike;
	vector<double> bid;
	vector<double> ask;
	vector<double> impVol;
};

#include "OptionData.hpp"
#endif