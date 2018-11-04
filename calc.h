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

__device__ bool zero(double in);

void listDir(char* dirPath, vector<char*>* v);

double* calcPearson(int nx, double* x, int* xDates, int ny, double* y, int* yDates);

int parseDate(char* date);

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

void addStrToVec(char*, vector<char*>*);