#include "AVData.h"

void AVData::tokenize(){
	if(isOpen()){
		while(vector<char*>* tokenized = this->getline()){
			if(!this->eof()){
				if(strcmp((*tokenized)[1], "") != 0)
					open.push_back(stod((*tokenized)[1]));
				if(strcmp((*tokenized)[2], "") != 0)
					high.push_back(stod((*tokenized)[2]));
				if(strcmp((*tokenized)[3], "") != 0)
					low.push_back(stod((*tokenized)[3]));
				if(strcmp((*tokenized)[4], "") != 0)
					close.push_back(stod((*tokenized)[4]));
				if(strcmp((*tokenized)[5], "") != 0)
					volume.push_back(stod((*tokenized)[5]));
			}
			else break;
		}
	}
}

AVData::AVData(char* fn) : CSVReader(fn){}

const vector<double>* AVData::price(){
	return &close;
}