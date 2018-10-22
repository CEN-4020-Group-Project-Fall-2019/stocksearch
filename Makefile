main: calc.h calc.cu
	nvcc -rdc=true -arch sm_61 -o calc calc.cu
debug: calc.h calc.cu
	nvcc -rdc=true -arch sm_61 -g -G -o calc calc.cu
