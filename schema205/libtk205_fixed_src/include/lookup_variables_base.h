#ifndef LOOKUP_VARIABLES_BASE_H_
#define LOOKUP_VARIABLES_BASE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <sstream>

class PerformanceMapBase;

template <class T>
using is_scoped_enum = std::integral_constant<bool, !std::is_convertible<T,int>{}
                                                  && std::is_enum<T>{}>;

// ------------------------------------------------------------------------------------------------
/// @class LookupVariablesBase lookup_variables_base.h

class LookupVariablesBase {

public:
    LookupVariablesBase() = default;
    virtual ~LookupVariablesBase() = default;
    LookupVariablesBase(const LookupVariablesBase& other) = default;
    LookupVariablesBase& operator=(const LookupVariablesBase& other) = default;

    virtual void populate_performance_map(PerformanceMapBase* performance_map) = 0;

    inline void add_data_table(PerformanceMapBase* performance_map, std::vector<double>& table)
    {
       performance_map->add_data_table(table);
    }

    template < class T, typename = std::enable_if<is_scoped_enum<T>::value> >
    void add_data_table(PerformanceMapBase* performance_map, std::vector<T>& table)
    {
        std::vector<double> converted_enums;
        std::transform(table.begin(), table.end(), std::back_inserter(converted_enums),
                 [](T n) { return static_cast<double>(n); });
        performance_map->add_data_table(converted_enums);
    }
};

#endif
