#include <iostream>
#include <fstream>
#include <vector>
#include <stdio.h>
#include <cstring>
#include <sys/types.h>
#include <dirent.h>
#include <time.h>

#include "AVData.h"
#include "OptionData.h"

using namespace std;

__device__ bool zero(double in);

void listDir(char* dirPath, vector<char*>* v);

double* calcPearson(int nx, double* x, int* xDates, int ny, double* y, int* yDates);

int parseDate(char* date);

void addStrToVec(char*, vector<char*>*);