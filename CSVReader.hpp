#include "CSVReader.h"
CSVReader::CSVReader(char* fn){
	setFile(fn);
}

void CSVReader::setFile(char* fn){
	file.open(fn);
	filename = fn;//memory leak, causes segfault if initialized from argv. Need to implement copy iterator for strings.
}

vector<char*>* CSVReader::getline(){
	vector<char*>* tokenized;
	if(!this->eof()){
		tokenized = new vector<char*>;//mem leak?
		if(!file.eof()){
			char* line = new char[256];
			file.getline(line, 256);
			tokenized->push_back(&line[0]);
			for(int i = 0; line[i] != '\0'; i++){
				if(line[i]==','){
					line[i] = '\0';
					tokenized->push_back(&line[i+1]);
				}
			}	
		}
	}
	return tokenized;	
}

bool CSVReader::eof(){
	return file.eof();
}

bool CSVReader::isOpen(){
	return file.is_open();
}

CSVReader::~CSVReader(){//eventually add delete[] filename;
	file.close();
}

CSVReader::CSVReader(const CSVReader& copy){
	filename = copy.filename;
	file.open(filename);
}

const char* CSVReader::fileName(){
	return filename;
}