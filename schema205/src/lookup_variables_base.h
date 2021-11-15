#ifndef LOOKUP_VARIABLES_BASE_H_
#define LOOKUP_VARIABLES_BASE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <sstream>
#include "error_handling_tk205.h"

class performance_map_base;

// ------------------------------------------------------------------------------------------------
/// @class lookup_variables_base lookup_variables_base.h
/// @note  If you are seeing this class in your build directory, it has been copied there from
///        a source location. Changes will not be saved!

class lookup_variables_base {

public:
    lookup_variables_base() = default;
    virtual ~lookup_variables_base() = default;
    lookup_variables_base(const lookup_variables_base& other) = default;
    lookup_variables_base& operator=(const lookup_variables_base& other) = default;

    virtual void Populate_performance_map(performance_map_base* performance_map) = 0;

    inline void Add_data_table(performance_map_base* performance_map, std::vector<double>& table)
    {
       performance_map->Add_data_table(table);
       std::ostringstream oss;
       oss << "Adding grid table with size " << table.size();
       tk205::Show_message(tk205::msg_severity::INFO_205, oss.str());
    }
};

#endif