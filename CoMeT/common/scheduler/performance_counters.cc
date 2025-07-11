#include "performance_counters.h"

#include <fstream>
#include <sstream>
#include <iostream>

using namespace std;

PerformanceCounters::PerformanceCounters(std::string instPowerFileName, std::string instTemperatureFileName, std::string instCPIStackFileName)
    : instPowerFileName(instPowerFileName), instTemperatureFileName(instTemperatureFileName), instCPIStackFileName(instCPIStackFileName) {

}

/** getPowerOfComponent
    Returns the latest power consumption of a component being tracked using base.cfg. Return -1 if power value not found.
*/
double PerformanceCounters::getPowerOfComponent (string component) const {
	ifstream powerLogFile(instPowerFileName);
	string header;
	string footer;

	if (powerLogFile.good()) {
		getline(powerLogFile, header);
		getline(powerLogFile, footer);
	}

	std::istringstream issHeader(header);
	std::istringstream issFooter(footer);
	std::string token;

	while(getline(issHeader, token, '\t')) {
		std::string value;
		getline(issFooter, value, '\t');
		if (token == component) {
			return stod (value);
		}
	}

	return -1;
}

/** getPowerOfCore
 * Return the latest total power consumption of the given core. Requires "tp" (total power) to be tracked in base.cfg. Return -1 if power is not tracked.
 */
double PerformanceCounters::getPowerOfCore(int coreId) const {
	string component = "C_" + std::to_string(coreId);
	return getPowerOfComponent(component);
}


/** getPeakTemperature
    Returns the latest peak temperature of any component
*/
double PerformanceCounters::getPeakTemperature () const {
	ifstream temperatureLogFile(instTemperatureFileName);
	string header;
	string footer;

	if (temperatureLogFile.good()) {
		getline(temperatureLogFile, header);
		getline(temperatureLogFile, footer);
	}

	std::istringstream issFooter(footer);

	double maxTemp = -1;
	std::string value;
	while(getline(issFooter, value, '\t')) {
		double t = stod (value);
		if (t > maxTemp) {
			maxTemp = t;
		}
	}

	return maxTemp;
}

/** getTemperatureOfComponent
    Returns the latest temperature of a component being tracked using base.cfg. Return -1 if power value not found.
*/
double PerformanceCounters::getTemperatureOfComponent (string component) const {
	ifstream temperatureLogFile(instTemperatureFileName);
	string header;
	string footer;

	if (temperatureLogFile.good()) {
		getline(temperatureLogFile, header);
		getline(temperatureLogFile, footer);
	}

	std::istringstream issHeader(header);
	std::istringstream issFooter(footer);
	std::string token;

	while(getline(issHeader, token, '\t')) {
		std::string value;
		getline(issFooter, value, '\t');

		if (token == component) {
			return stod (value);
		}
	}

	return -1;
}

/** getTemperatureOfCore
 * Return the latest temperature of the given core. Requires "tp" (total power) to be tracked in base.cfg. Return -1 if power is not tracked.
 */
double PerformanceCounters::getTemperatureOfCore(int coreId) const {
	string component = "C_" + std::to_string(coreId);
	return getTemperatureOfComponent(component);
}

/** getTemperatureOfBank
 * Return the latest temperature of the given memory bank. Requires "tp" (total power) to be tracked in base.cfg. Return -1 if power is not tracked.
 */
double PerformanceCounters::getTemperatureOfBank(int bankId) const {
	string component = "B_" + std::to_string(bankId);
	return getTemperatureOfComponent(component);
}

vector<string> PerformanceCounters::getCPIStackParts() const {
	ifstream cpiStackLogFile(instCPIStackFileName);
    string line;
	std::istringstream issLine;

	vector<string> parts;
	if (cpiStackLogFile.good()) {
		getline(cpiStackLogFile, line); // consume first line containing the CSV header
		getline(cpiStackLogFile, line); // consume second line containing total values
		while (cpiStackLogFile.good()) {
			getline(cpiStackLogFile, line);
			issLine.str(line);
			issLine.clear();
			std::string m;
			getline(issLine, m, '\t');
			if (m.length() > 0) {
				parts.push_back(m);
			}
		}
	}
	return parts;
}

/**
 * Get a performance metric for the given core.
 * Available performance metrics can be checked in InstantaneousPerformanceCounters.log
 */
double PerformanceCounters::getCPIStackPartOfCore(int coreId, std::string metric) const {
	ifstream cpiStackLogFile(instCPIStackFileName);
    string line;
	std::istringstream issLine;

	// first find the line in the logfile that contains the desired metric
	bool metricFound = false;
	while (!metricFound) {
		if (cpiStackLogFile.good()) {
			getline(cpiStackLogFile, line);
			issLine.str(line);
			issLine.clear();
			std::string m;
			getline(issLine, m, '\t');
			metricFound = (m == metric);
		} else {
			return 0;
		}
	}

	// then split the coreId-th value from this line (first value is metric name, but already consumed above)
	std::string value;
	for (int i = 0; i < coreId + 1; i++) {
		getline(issLine, value, '\t');
		if ((i == 0) && (value == "-")) {
			return 0;
		}
	}

	return stod(value);
}

/**
 * Get the utilization of the given core.
 */
double PerformanceCounters::getUtilizationOfCore(int coreId) const {
	float cpi = 0;
	float mem_l1d = 0;

	float itlb = 0;
	float branch = 0;
	float issue = 0;
	float depend_branch = 0;
	float depend_fp = 0;
	float depend_int = 0;

	float mem_dram = 0;
	float ifetch = 0;
	for (const string & part : getCPIStackParts()) {
		// exclude non-memory-related parts
		if ((part.find("mem") == std::string::npos) &&
		    (part.find("ifetch") == std::string::npos) &&
		    (part.find("sync") == std::string::npos) &&
		    (part.find("dvfs-transition") == std::string::npos) &&
		    (part.find("imbalance") == std::string::npos) &&
		    (part.find("other") == std::string::npos)) {

			cpi += getCPIStackPartOfCore(coreId, part);
		}
		if (part.find("mem-l1d") != std::string::npos){
			mem_l1d += getCPIStackPartOfCore(coreId, part);
		}

		if (part.find("itlb") != std::string::npos){
			itlb += getCPIStackPartOfCore(coreId, part);
		}

		if (part.find("branch") != std::string::npos){
			branch += getCPIStackPartOfCore(coreId, part);
		}
		if (part.find("issue") != std::string::npos){
			issue += getCPIStackPartOfCore(coreId, part);
		}
		if (part.find("depend-branch") != std::string::npos){
			depend_branch += getCPIStackPartOfCore(coreId, part);
		}
		if (part.find("depend-fp") != std::string::npos){
			depend_fp += getCPIStackPartOfCore(coreId, part);
		}
		if (part.find("depend-int") != std::string::npos){
			depend_int += getCPIStackPartOfCore(coreId, part);
		}

		if (part.find("mem-dram") != std::string::npos){
			mem_dram += getCPIStackPartOfCore(coreId, part);
		}
		if (part.find("ifetch") != std::string::npos){
			ifetch += getCPIStackPartOfCore(coreId, part);
		}
	}
	float total = getCPIOfCore(coreId);
	//printf("******************************************************** \n" );
	//printf("******************************************************** \n" );
	//printf("******************************************************** \n" );
        printf("The cpi_core in core %d is %f; \t",coreId , cpi );
        printf("The Total is %f; \n", total  );
        //printf("******************************************************** \n" );
        //printf("The itlb  is %f \n", itlb);
        //printf("The branch is %f \n", branch);
        //printf("The issue  is %f \n", issue);
        //printf("The depend_branch  is %f \n", depend_branch);
        //printf("The depend_fp  is %f \n", depend_fp);
        //printf("The depend_int  is %f \n", depend_int);
        //printf("******************************************************** \n" );
        //printf("The mem_dram  is %f \t", mem_dram );
        //printf("The ifetch  is %f \n",  ifetch );
	return cpi / total;
}

/**
 * Get the CPI of the given core.
 */
double PerformanceCounters::getCPIOfCore(int coreId) const {
	return getCPIStackPartOfCore(coreId, "total");
}

/**
 * Get the frequency of the given core.
 */
int PerformanceCounters::getFreqOfCore(int coreId) const {
	if (coreId >= (int)frequencies.size()) {
		return -1;
	} else {
		return frequencies.at(coreId);
	}
}

/**
 * Notify new frequencies
 */
void PerformanceCounters::notifyFreqsOfCores(std::vector<int> newFrequencies) {
	frequencies = newFrequencies;
}

/**
 * Get the frequency of the given core.
 */
double PerformanceCounters::getIPSOfCore(int coreId) const {
	return 1e6 * getFreqOfCore(coreId) / getCPIOfCore(coreId);
}
