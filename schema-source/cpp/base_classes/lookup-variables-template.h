#ifndef LOOKUP_VARIABLES_TEMPLATE_H_
#define LOOKUP_VARIABLES_TEMPLATE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <sstream>
#include "performance-map-template.h"

namespace fan_spec {
  namespace ashrae205 {

template <class T>
using is_scoped_enum = std::integral_constant<bool, !std::is_convertible<T,int>{}
                                                  && std::is_enum<T>{}>;

// ------------------------------------------------------------------------------------------------
/// @class LookupVariablesTemplate lookup_variables_base.h

class LookupVariablesTemplate {

public:
    LookupVariablesTemplate() = default;
    virtual ~LookupVariablesTemplate() = default;
    LookupVariablesTemplate(const LookupVariablesTemplate& other) = default;
    LookupVariablesTemplate& operator=(const LookupVariablesTemplate& other) = default;

    virtual void populate_performance_map(ashrae205::PerformanceMapTemplate* performance_map) = 0;

    inline void add_data_table(ashrae205::PerformanceMapTemplate* performance_map, std::vector<double>& table)
    {
       performance_map->add_data_table(table);
    }

    template < class T, typename = std::enable_if<is_scoped_enum<T>::value> >
    void add_data_table(PerformanceMapTemplate* performance_map, std::vector<T>& table)
    {
        std::vector<double> converted_enums;
        std::transform(table.begin(), table.end(), std::back_inserter(converted_enums),
                 [](T n) { return static_cast<double>(n); });
        performance_map->add_data_table(converted_enums);
    }
};
}
}
#endif
