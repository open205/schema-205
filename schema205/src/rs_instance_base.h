#ifndef RS_INSTANCE_BASE_H_
#define RS_INSTANCE_BASE_H_

#include <nlohmann/json.hpp>
#include <fstream>

/// @class RSInstanceBase RS_instance_base.h
/// @brief This class isolates derived RS classes from their owner (ASHRAE205). It handles
///        no resources.
/// @note  If you are seeing this class in your build directory, it has been copied there from
///        a source location. Changes will not be saved!

namespace tk205  {

    class RSInstanceBase
    {
    public:

        RSInstanceBase() = default;
        virtual ~RSInstanceBase() = default;
        RSInstanceBase(const RSInstanceBase& other) = default;
        RSInstanceBase& operator=(const RSInstanceBase& other) = default;
        RSInstanceBase(RSInstanceBase&&) = default;
        RSInstanceBase& operator=(RSInstanceBase&&) = default;

        virtual void initialize(const nlohmann::json& j) = 0;
    };
}

#endif