#ifndef PERFORMANCE_MAP_BASE_H_
#define PERFORMANCE_MAP_BASE_H_

#include <memory>
#include <vector>
#include <iostream>

// ------------------------------------------------------------------------------------------------
/// @class performance_map_base performance_map_base.h

class performance_map_base {

public:
    performance_map_base() = default;
    virtual ~performance_map_base() = default;
    performance_map_base(const performance_map_base& other) = default;
    performance_map_base& operator=(const performance_map_base& other) = default;

    //private btwxt instance to collect grid and tables for a single performance map
    //public Calculate_performance(target)
};

#endif