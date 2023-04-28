#ifndef PERFORMANCE_MAP_BASE_H_
#define PERFORMANCE_MAP_BASE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <nlohmann/json.hpp>
#include <courierr/courierr.h>
#include <btwxt.h>

// ------------------------------------------------------------------------------------------------
/// @class PerformanceMapBase performance_map_base.h

class PerformanceMapBase {

//namespace Courierr { class Courierr; };

public:
    PerformanceMapBase() = default;
    virtual ~PerformanceMapBase() = default;
    PerformanceMapBase(const PerformanceMapBase& other) = delete;
    PerformanceMapBase& operator=(const PerformanceMapBase& other) = delete;
    PerformanceMapBase(PerformanceMapBase&& other) = default;
    PerformanceMapBase& operator=(PerformanceMapBase&& other) = default;

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	j
  // ----------------------------------------------------------------------------------------------
    virtual void initialize(const nlohmann::json& j, std::shared_ptr<::Courierr::Courierr> logger) = 0;

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	axis TBD
  // ----------------------------------------------------------------------------------------------
    inline void add_grid_axis(std::vector<double>& axis) {
        grid_axes.emplace_back(axis);
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	axis TBD
  // ----------------------------------------------------------------------------------------------
    inline void add_grid_axis(std::vector<int>& axis) {
        grid_axes.emplace_back(std::vector<double>(axis.begin(), axis.end()));
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	table TBD
  // ----------------------------------------------------------------------------------------------
    inline void add_data_table(std::vector<double>& table) {
        btwxt->add_grid_point_data_set(table);
    }
    
  // ----------------------------------------------------------------------------------------------
  /// @brief	
  // ----------------------------------------------------------------------------------------------
    inline void finalize_grid() {
        btwxt = std::make_unique<Btwxt::RegularGridInterpolator>(grid_axes, courier);
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	table_index TBD
  // ----------------------------------------------------------------------------------------------
    inline double calculate_performance(const std::vector<double> &target,
                                        std::size_t table_index,
                                        Btwxt::Method performance_interpolation_method = Btwxt::Method::linear)
    {
        for (auto i = 0u; i < grid_axes.size(); i++)
        {
            btwxt->set_axis_interpolation_method(i, performance_interpolation_method);
        }
        return btwxt->get_value_at_target(target, table_index);
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	Using pre-populated grid axes and lookup tables, calculate a set of performance
  ///         results.
  /// @param	target 
  // ----------------------------------------------------------------------------------------------
    inline std::vector<double> calculate_performance(const std::vector<double> &target,
                                                     Btwxt::Method performance_interpolation_method = Btwxt::Method::linear)
    {
        for (auto i = 0u; i < grid_axes.size(); i++)
        {
            btwxt->set_axis_interpolation_method(i, performance_interpolation_method);
        }
        return btwxt->get_values_at_target(target);
    }

private:
    std::unique_ptr<Btwxt::RegularGridInterpolator> btwxt;
    std::vector<std::vector<double>> grid_axes;
    std::shared_ptr<Courierr::Courierr> courier{std::make_shared<Courierr::SimpleCourierr>()};
};

#endif