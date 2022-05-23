#ifndef RS_INSTANCE_FACTORY_H_
#define RS_INSTANCE_FACTORY_H_

#include <string>
#include <memory>
#include "rs_instance_base.h" // definition req'd for unique_ptr

/// @class rs_instance_factory rs_instance_factory.h
/// @brief This class is an abstract interface to support RS factory sub-classes
/// @note  If you are seeing this class in your build directory, it has been copied there from
///        a source location. Changes will not be saved!

namespace tk205  {
   class rs_instance_factory
   {
   public: // Interface

      rs_instance_factory() = default;
      virtual ~rs_instance_factory() = default;

      static bool Register_factory(std::string const &RS_ID,
                                   std::shared_ptr<rs_instance_factory> factory);

      // Universal factory interface Create(). Factory::Create() will, through delegation,
      // actually return the requested object.
      static std::unique_ptr<rs_instance_base> Create(std::string const &RS_ID,
                                                      const char* RS_instance_file);

      // Derived factories override Create_instance() for actual resource creation
      virtual std::unique_ptr<rs_instance_base> Create_instance(const char* RS_instance_file) const = 0;

      // Rule of five
      rs_instance_factory(const rs_instance_factory& other) = delete;
      rs_instance_factory& operator=(const rs_instance_factory& other) = delete;
      rs_instance_factory(rs_instance_factory&&) = delete;
      rs_instance_factory& operator=(rs_instance_factory&&) = delete;
   };
}

#endif 