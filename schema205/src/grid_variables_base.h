#ifndef GRID_VARIABLES_BASE_H_
#define GRID_VARIABLES_BASE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <sstream>

#include <performance_map_base.h>
#include <error_handling_tk205.h>

// ------------------------------------------------------------------------------------------------
/// @class grid_variables_base grid_variables_base.h
/// @note  If you are seeing this class in your build directory, it has been copied there from
///        a source location. Changes will not be saved!

class grid_variables_base {

public:
    grid_variables_base() = default;
    virtual ~grid_variables_base() = default;
    grid_variables_base(const grid_variables_base& other) = default;
    grid_variables_base& operator=(const grid_variables_base& other) = default;

    virtual void Populate_performance_map(performance_map_base* performance_map) = 0;

    inline void Add_grid_axis(performance_map_base* performance_map, std::vector<double>& axis)
    {
       performance_map->Add_grid_axis(axis);
       std::ostringstream oss;
       oss << "Adding grid axis with size " << axis.size();
       tk205::Show_message(tk205::msg_severity::INFO_205, oss.str());
    }
    inline void Add_grid_axis(performance_map_base* performance_map, std::vector<int>& axis)
    {
       performance_map->Add_grid_axis(axis);
       std::ostringstream oss;
       oss << "Adding (int) grid axis with size " << axis.size();
       tk205::Show_message(tk205::msg_severity::INFO_205, oss.str());
    }
};

#endif