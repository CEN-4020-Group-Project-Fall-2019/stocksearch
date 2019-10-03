#ifndef AVDATA_H
#define AVDATA_H

//designed to read from alphavantage, need to update for yahoo info

#include "CSVReader.h"
class AVData : public CSVReader{
public:
	AVData(char* fn);
	void tokenize();
	const vector<double>* price();
private:
	vector<int> timestamp;
	vector<double> open;
	vector<double> high;
	vector<double> low;
	vector<double> close;
	vector<double> volume;
};

#include "AVData.hpp"
#endif