/**
 * This header implements the GDP power DVFS policy
 */

#ifndef __DVFS_GDP_H
#define __DVFS_GDP_H

#include <vector>
#include "dvfspolicy.h"
// the .h add for GDP 
#include "performance_counters.h"
// .h add end

class DVFSGDP : public DVFSPolicy {
public:
    DVFSGDP(
                    const PerformanceCounters *performanceCounters,
                    int coreRows,
                    int coreColumns,
                    int minFrequency,
                    int maxFrequency,
                    int frequencyStepSize);

    virtual std::vector<int> getFrequencies(
                    const std::vector<int> &oldFrequencies,
                    const std::vector<bool> &activeCores);

private:
    const PerformanceCounters *performanceCounters;
    unsigned int coreRows;
    unsigned int coreColumns;
    int minFrequency;
    int maxFrequency;
    int frequencyStepSize;
};

#endif


