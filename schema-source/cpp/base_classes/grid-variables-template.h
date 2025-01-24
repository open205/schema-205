#ifndef GRID_VARIABLES_BASE_H_
#define GRID_VARIABLES_BASE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <sstream>

#include <performance-map-template.h>
#include <btwxt/grid-axis.h>

namespace fan_spec {
  namespace ashrae205 {


// ------------------------------------------------------------------------------------------------
/// @class GridVariablesTemplate grid_variables_base.h

class GridVariablesTemplate {

public:
    GridVariablesTemplate() = default;
    virtual ~GridVariablesTemplate() = default;
    GridVariablesTemplate(const GridVariablesTemplate& other) = default;
    GridVariablesTemplate& operator=(const GridVariablesTemplate& other) = default;

    virtual void populate_performance_map(ashrae205::PerformanceMapTemplate* performance_map) = 0;

    inline void add_grid_axis(ashrae205::PerformanceMapTemplate* performance_map, std::vector<double>& axis)
    {
       performance_map->add_grid_axis(axis);
    }
    inline void add_grid_axis(ashrae205::PerformanceMapTemplate* performance_map, std::vector<int>& axis)
    {
       performance_map->add_grid_axis(axis);
    }
};
  }
}
#endif
