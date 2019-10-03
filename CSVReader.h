#ifndef CSVREADER_H
#define CSVREADER_H

#include <iostream>
#include <fstream>
#include <vector>
#include <stdio.h>
#include <cstring>
#include <sys/types.h>
#include <dirent.h>
#include <time.h>

using namespace std;

class CSVReader{
public:
	CSVReader();
	CSVReader(char* file);
	void setFile(char* file);
	CSVReader(const CSVReader &);
	~CSVReader();
	vector<char*>* getline();
	const char* fileName();
	bool eof();
	bool isOpen();
protected:
	ifstream file;
	char* filename;
};

#include "CSVReader.hpp"

#endif