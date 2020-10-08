#include "RS_instance_factory.h"

class RS0001_factory : public RS_instance_factory
{
   public:

      std::unique_ptr<RS_instance_base> Create() const override;

   private:
      // Implementation of self-registering class
      // a la https://www.bfilipek.com/2018/02/factory-selfregister.html
      static bool s_registered;
};
