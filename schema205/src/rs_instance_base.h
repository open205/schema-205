#ifndef RS_INSTANCE_BASE_H_
#define RS_INSTANCE_BASE_H_

#include <nlohmann/json.hpp>
#include <fstream>

/// @class RS_instance_base RS_instance_base.h
/// @brief This class isolates derived RS classes from their owner (ASHRAE205). It handles
///        no resources.
/// @note  If you are seeing this class in your build directory, it has been copied there from
///        a source location. Changes will not be saved!

namespace tk205  {

    class rs_instance_base
    {
    public:

        rs_instance_base() = default;
        virtual ~rs_instance_base() = default;
        rs_instance_base(const rs_instance_base& other) = default;
        rs_instance_base& operator=(const rs_instance_base& other) = default;
        rs_instance_base(rs_instance_base&&) = default;
        rs_instance_base& operator=(rs_instance_base&&) = default;

        virtual void Initialize(const nlohmann::json& j) = 0;
    };
}

#endif