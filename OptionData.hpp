#include "OptionData.h"
OptionData::OptionData(char* fn) : CSVReader(fn){}

void OptionData::tokenize(){
	if(isOpen()){
		time_t curTime = time(0);
		while(vector<char*>* tokenized = this->getline()){
			if(!this->eof()){

				call.push_back((strcmp((*tokenized)[0], "C") == 0));
				exp.push_back((stod((*tokenized)[1])+16*3600 - curTime)/(365*24*60*60));
				strike.push_back(stod((*tokenized)[2]));
				bid.push_back(stod((*tokenized)[3]));
				ask.push_back(stod((*tokenized)[4]));
				impVol.push_back(stod((*tokenized)[5]));

			}
			else break;
		}
	}
}

bool* OptionData::comparePrices(double* optionPrices){
	bool* temp = new bool[ask.size()];
	for(int i = 0; i < ask.size(); i++){
		temp[i] = optionPrices[i] < ask[i];
		if(call[i] && temp[i])
			printf("%s %f %f %f %f %f\n", this->fileName(), exp[i], strike[i], optionPrices[i], ask[i], bid[i]);
	}
	return temp;
}