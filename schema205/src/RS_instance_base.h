#ifndef RS_INSTANCE_BASE_H_
#define RS_INSTANCE_BASE_H_

#include <nlohmann/json_fwd.hpp>

/// @class RS_instance_base RS_instance_base.h
/// @brief This class isolates derived RS classes from their owner (ASHRAE205). It handles
///        no resources.

class RS_instance_base
{
public:

    RS_instance_base() = default;
    virtual ~RS_instance_base() = default;
    RS_instance_base(const RS_instance_base& other) = delete;
    RS_instance_base& operator=(const RS_instance_base& other) = delete;
    RS_instance_base(RS_instance_base&&) = delete;
    RS_instance_base& operator=(RS_instance_base&&) = delete;

    virtual void Initialize(const nlohmann::json& j) { }
};

#endif