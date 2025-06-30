#include "dramLowpower.h"
#include <iomanip>
#include <iostream>
#include <map>

#include <sstream>
#include <fstream>
#include <string>

#include <algorithm>

using namespace std;

DramLowpower::DramLowpower(
        const PerformanceCounters *performanceCounters,
        int numberOfBanks,
        float dtmCriticalTemperature,
        float dtmRecoveredTemperature)
    : performanceCounters(performanceCounters),
      numberOfBanks(numberOfBanks),
      dtmCriticalTemperature(dtmCriticalTemperature),
      dtmRecoveredTemperature(dtmRecoveredTemperature) {

}

/*
Return the new memory modes, based on current temperatures.
*/
std::map<int,int> DramLowpower::getNewBankModes(std::map<int, int> old_bank_modes) {

    cout << "in DramLowpower::getNewBankModes\n";
    std::map<int,int> new_bank_mode_map;

///////////////////////////////////////////////////////
// method_3 : Round Robin Method 
///////////////////////////////////////////////////////
    std::vector<double> old_bank_temperature(numberOfBanks);
	
    // Firstly,get all bank_temperature and their max_temperature
    for (int i = 0; i < numberOfBanks; i++){
   	old_bank_temperature[i]  =  performanceCounters->getTemperatureOfBank(i) ;
    }
    std::vector<std::pair<int, double>> temp_vector;
    for (int i = 0; i < numberOfBanks; i++) {
	    temp_vector.push_back(std::make_pair(i, old_bank_temperature[i]));
    }

    // Sort the temperature
    //std::vector<std::pair<int, float>> new_temp_vector(old_bank_temperature.begin(), old_bank_temperature.end());
    auto sort_by_value_descending = [](const std::pair<int, double>& a, const std::pair<int, double>& b) {
	    return a.second > b.second;  // 
    };

    std::sort(temp_vector.begin(), temp_vector.end(), sort_by_value_descending);

    std::vector<int> sorted_keys;
    for (const auto& pair : temp_vector) {
        sorted_keys.push_back(pair.first);
    }
    // Get the max temperature of Banks
    int max_temp_bank_id = temp_vector[0].first;  // ID of the Bank in  max temperature
    float max_temperature = temp_vector[0].second;  // Max Temperature
						     //
    // number of channels that should set LOWPOWER
    int N_RR_Mem;
    float thermal_limit_Mem = dtmCriticalTemperature - 2;
    float max_temperature_Mem = max_temperature;
    if (max_temperature_Mem >= thermal_limit_Mem)
	  //N_RR_Mem = 16;
	    //N_RR_Mem = 4; // for streamcluster
	    N_RR_Mem = 7; // for bodytrack
    else if (max_temperature_Mem >= (thermal_limit_Mem -0.5))
	    N_RR_Mem = 4;
    else if (max_temperature_Mem >= (thermal_limit_Mem -1.0))
	    N_RR_Mem = 2;
    else if (max_temperature_Mem >= (thermal_limit_Mem -1.5))
	    N_RR_Mem = 1;
    else  if (max_temperature_Mem >= (thermal_limit_Mem -2.0))
	    N_RR_Mem = 0;
    else if (max_temperature_Mem >= (thermal_limit_Mem -2.5))
	    N_RR_Mem = 0;
    else  if (max_temperature_Mem >= (thermal_limit_Mem -3.0))
	    N_RR_Mem = 0;
    else if (max_temperature_Mem >= (thermal_limit_Mem -3.5))
	    N_RR_Mem = 0;
    else if (max_temperature_Mem >= (thermal_limit_Mem -4.0))
	    N_RR_Mem = 0;
    else
	N_RR_Mem = 0;

    // Set All Banks NORMAL_POWER
    for (int i = 0; i < numberOfBanks; i++)
    {
	    new_bank_mode_map[i] = NORMAL_POWER;
    }
    // Set N_RR_Mem banks to LOW_POWER
    int N_RR = 0;
    int index_bank ;
    while (N_RR < N_RR_Mem){
	    index_bank = sorted_keys[N_RR];
	    new_bank_mode_map[index_bank] = LOW_POWER;
	    N_RR = N_RR + 1;
    }

	///////////////////////////////////////////////////////
	// method_1 : original methof
	///////////////////////////////////////////////////////
    // for (int i = 0; i < numberOfBanks; i++)
    // {
    //     if (old_bank_modes[i] == LOW_POWER) // if the memory was already in low power mode
    //     {
    //         if (performanceCounters->getTemperatureOfBank(i) < dtmRecoveredTemperature) // temp dropped below recovery temperature
    //         {
    //             cout << "[Scheduler][dram-DTM]: thermal violation ended for bank " << i << endl;
    //             new_bank_mode_map[i] = NORMAL_POWER;
    //         }
    //         else
    //         {
    //     	    new_bank_mode_map[i] = LOW_POWER;
    //         }
    //     }
    //     else // if the memory was not in low power mode
    //     {
    //     	if (performanceCounters->getTemperatureOfBank(i) > dtmCriticalTemperature) // temp is above critical temperature
    //     	{
    //     		cout << "[Scheduler][dram-DTM]: thermal violation detected for bank " << i << endl;
    //     		new_bank_mode_map[i] = LOW_POWER;
    //     	}
    //     	else
    //     	{
    //     		new_bank_mode_map[i] = NORMAL_POWER;
    //     	}
    //     }
    // }
    


	///////////////////////////////////////////////////////
	// method_2 : original methof
	///////////////////////////////////////////////////////
	// XJY add 3D-GDP LOWPOWER Policy here
	//std::string filename = "./system_sim_state/mapping.txt";
	//std::ifstream infile(filename);
	//if (!infile.is_open()) {
	//	std::cerr << "Error: Could not open file " << filename << std::endl;
	//}

	//std::string line;
	//if (std::getline(infile, line)) {
	//	// std::map<int, int> new_bank_modes_map;
	//	std::istringstream iss(line);
	//	int index = 0;
	//	int key;
	//	int value;

	//	// Parse the line into the map
	//	while (iss >> value) {
	//		//if (value == 0)
	//		if (value == 1.00)
	//			new_bank_mode_map[index] = LOW_POWER;
	//		else
	//			new_bank_mode_map[index] = NORMAL_POWER;
	//		++index;
	//	}
	//	// Print the map to verify
	//	for (const auto& pair : new_bank_mode_map) {
	//		std::cout << "Index: " << pair.first << ", Value: " << pair.second << std::endl;
	//	}
	//} else {
	//	std::cerr << "Error: Could not read the first line from file." << std::endl;
	//}
	//infile.close();
	// XJY ADD Code END Here

    return new_bank_mode_map;
}
