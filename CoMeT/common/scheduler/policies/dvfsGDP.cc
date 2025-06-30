#include "dvfsGDP.h"
#include "powermodel.h"
#include <iomanip>
#include <iostream>
#include <fstream>


using namespace std;

DVFSGDP::DVFSGDP(const PerformanceCounters *performanceCounters, int coreRows, int coreColumns, int minFrequency, int maxFrequency, int frequencyStepSize)
	: performanceCounters(performanceCounters), coreRows(coreRows), coreColumns(coreColumns), minFrequency(minFrequency), maxFrequency(maxFrequency), frequencyStepSize(frequencyStepSize){

	}

std::vector<int> DVFSGDP::getFrequencies(const std::vector<int> &oldFrequencies, const std::vector<bool> &activeCores) {
	std::vector<int> frequencies(coreRows * coreColumns);

	/* GDP core code begin */

	unsigned int n_core = coreColumns * coreRows;
	std::vector<float> gdp(n_core, 0); // vector used to store the gdp power budget for each core




	/////////////////////////////////
	/// Get Core State from CoreMemDTM
	/////////////////////////////////
	string corememdtm = "../common/scheduler/policies/CoreMemDTM.py";
	string command_dtm = "python3 "+ corememdtm;
	system(command_dtm.c_str());

	std::vector<float> core_state(n_core, 0); 
	ifstream file_core_state("./CoreMemDTM/core_state.txt");
	for (unsigned int coreCounter = 0; coreCounter < n_core; coreCounter++)
	{
			file_core_state >> core_state.at(coreCounter);
			//cout << "get core state" << endl;
			//cout << core_state.at(coreCounter) << endl;
	}
	file_core_state.close();

	/////////////////////////////////
	/// Get Core State from CoreMemDTM
	/////////////////////////////////

////////////////////////////////////////////////
////////////////////////////////////////////////
	int Freq_ACTIVE = 3600;	
	int Freq_F1 = 3400;	
	int Freq_F2 = 3200;	
	int Freq_F3 = 3000;	
	int Freq_LOWPOWER = 2700;	

        string filename = "./CoreMemDTM/benchmark_name.py ";
        string command = "python3 "+filename;
        system(command.c_str());

	std::string mapping_name;
	std::ifstream mappingfile("./CoreMemDTM/benchmark_name.txt");
	if (!mappingfile.is_open()) {
	    std::cerr << "Error: Cannot open file.\n";
	    //return 1;
	}
	std::getline(mappingfile, mapping_name);
	mappingfile.close();
	mapping_name.erase(mapping_name.find_last_not_of(" \n\r\t") + 1);

	if (mapping_name == "swaption"){
		Freq_ACTIVE = 3600;	
		Freq_F1 = 3400;	
		Freq_F2 = 3200;	
		Freq_F3 = 3000;	
		Freq_LOWPOWER = 2700;	
	}
	else if (mapping_name == "blackscholes"){
		Freq_ACTIVE = 3600;	
		Freq_F1 = 3400;	
		Freq_F2 = 3200;	
		Freq_F3 = 3000;	
		Freq_LOWPOWER = 2700;	
	}
	else if (mapping_name == "bodytrack"){
		Freq_ACTIVE = 3000;	
		Freq_F1 = 2700;	
		Freq_F2 = 2400;	
		Freq_F3 = 2200;	
		Freq_LOWPOWER = 1500;	
	}
	else if (mapping_name == "streamcluster"){
		Freq_ACTIVE = 2700;	
		Freq_F1 = 2500;	
		Freq_F2 = 2300;	
		Freq_F3 = 2200;	
		Freq_LOWPOWER = 1500;	
	}
	else if (mapping_name == "dedup"){
		Freq_ACTIVE = 2700;	
		Freq_F1 = 2500;	
		Freq_F2 = 2300;	
		Freq_F3 = 2200;	
		Freq_LOWPOWER = 1500;	
	}

	//int Freq_ACTIVE = 2700;	
	//int Freq_F1 = 2500;	
	//int Freq_F2 = 2300;	
	//int Freq_F3 = 2000;	
	//int Freq_LOWPOWER = 1800;	


	/////////////////////////////////////
	// Get the Frequency
	/////////////////////////////////////
	//for blackschoels , swaptions , radiosity for core3-core7
	/////////////////////////////////////
	//int Freq_ACTIVE = 3600;	
	//int Freq_F1 = 3400;	
	//int Freq_F2 = 3200;	
	//int Freq_F3 = 3000;	
	//int Freq_LOWPOWER = 2700;	
	/////////////////////////////////////
	//for blackschoels , swaptions , radiosity for core12
	/////////////////////////////////////
	//int Freq_ACTIVE = 3400;	
	//int Freq_F1 = 3100;	
	//int Freq_F2 = 2800;	
	//int Freq_F3 = 2500;	
	//int Freq_LOWPOWER = 2000;	
	//
	/////////////////////////////////////
	//for bodytrack 
	///////////////////////////////////
	//int Freq_ACTIVE = 3000;	
	//int Freq_F1 = 2700;	
	//int Freq_F2 = 2400;	
	//int Freq_F3 = 2200;	
	//int Freq_LOWPOWER = 1500;	
	/////////////////////////////////////
	//for streamcluster
	/////////////////////////////////////
	// 
	//int Freq_ACTIVE = 3000;	
	//int Freq_F1 = 2900;	
	//int Freq_F2 = 2700;	
	//int Freq_F3 = 2600;	
	//int Freq_LOWPOWER = 2000;	
	//int Freq_ACTIVE = 2700;	
	//int Freq_F1 = 2500;	
	//int Freq_F2 = 2300;	
	//int Freq_F3 = 2000;	
	//int Freq_LOWPOWER = 1800;	

	float STATE_ACTIVE = 0.0;	
	float STATE_F1 = 1.0;	
	float STATE_F2 = 2.0;	
	float STATE_F3 = 3.0;	
	float STATE_LOWPOWER = 4.0;	

	for (unsigned int coreCounter = 0; coreCounter < coreRows * coreColumns; coreCounter++) {
		if (activeCores.at(coreCounter)) {
			float power = performanceCounters->getPowerOfCore(coreCounter);
        	        float temperature = performanceCounters->getTemperatureOfCore(coreCounter);
                        float utilization = performanceCounters->getUtilizationOfCore(coreCounter);
			int frequency = oldFrequencies.at(coreCounter);
			cout << "[Scheduler] [CoreMemDTM]: Core " << setw(2) << coreCounter << ":";
			cout << " f=" << frequency << " MHz";
			cout << " P=" << fixed << setprecision(3) << power << " W";
			cout << " T=" << fixed << setprecision(1) << temperature << " °C";
			cout << " utilization=" << fixed << setprecision(3) << utilization  << "";
			cout << " CoreMemDTM_Core_STATE =" << core_state.at(coreCounter) << endl;

			if(float(core_state.at(coreCounter)) == STATE_ACTIVE)	
				frequencies.at(coreCounter) = Freq_ACTIVE;
			if(float(core_state.at(coreCounter)) == STATE_F1)	
				frequencies.at(coreCounter) = Freq_F1;
			if(float(core_state.at(coreCounter)) == STATE_F2)	
				frequencies.at(coreCounter) = Freq_F2;
			if(float(core_state.at(coreCounter)) == STATE_F3)	
				frequencies.at(coreCounter) = Freq_F3;
			if(float(core_state.at(coreCounter)) == STATE_LOWPOWER)	
				frequencies.at(coreCounter) = Freq_LOWPOWER;

		}
	}

	return frequencies;
}
