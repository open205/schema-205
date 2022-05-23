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

   void Read_binary_file(const char* filename, std::vector<char> &bytes)
   {
      std::ifstream is (filename, std::ifstream::binary);
      if (is) 
      {
            // get length of file:
            is.seekg(0, is.end);
            size_t length = static_cast<size_t>(is.tellg());
            is.seekg(0, is.beg);

            bytes.resize(length);
            // read data as a block:
            is.read(bytes.data(), length);

            is.close();
      }
   }

   nlohmann::json Load_json(const char* input_file)
   {
      std::string filename(input_file);
      std::string::size_type idx = filename.rfind('.');

      using namespace nlohmann;
      
      json j;

      if(idx != std::string::npos)
      {
            std::string extension = filename.substr(idx+1);

            if (extension == "cbor")
            {
               std::vector<char> bytearray;
               Read_binary_file(input_file, bytearray);
               j = json::from_cbor(bytearray);
            }
            else if (extension == "json")
            {
               std::string schema(input_file);
               std::ifstream in(schema);
               in >> j;
            }
      }
      return j;
   }

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