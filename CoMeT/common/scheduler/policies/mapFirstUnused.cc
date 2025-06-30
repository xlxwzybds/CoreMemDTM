#include "mapFirstUnused.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>

MapFirstUnused::MapFirstUnused(unsigned int numberOfCores, std::vector<int> preferredCoresOrder)
	: numberOfCores(numberOfCores), preferredCoresOrder(preferredCoresOrder) {
	for (unsigned int i = 0; i < numberOfCores; i++) {
		if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), i) == this->preferredCoresOrder.end()) {
			this->preferredCoresOrder.push_back(i);
		}
	}
		//if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 0) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(0);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 5) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(5);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 10) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(10);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 2) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(2);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 7) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(7);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 8) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(8);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 13) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(13);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 15) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(15);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 1) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(1);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 4) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(4);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 6) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(6);
                //}
                //if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), 14) == this->preferredCoresOrder.end()) {
                //        this->preferredCoresOrder.push_back(14);
                //}
}

std::vector<int> MapFirstUnused::map(String taskName, int taskCoreRequirement, const std::vector<bool> &availableCores, const std::vector<bool> &activeCores) {
	std::vector<int> cores;

	// try to fill with preferred cores
	for (const int &c : preferredCoresOrder) {
		if (availableCores.at(c)) {
			cores.push_back(c);
			if ((int)cores.size() == taskCoreRequirement) {
				return cores;
			}
		}
	}

	std::vector<int> empty;
	return empty;
}
