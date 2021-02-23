"""
Markdown rendering utilities.
"""
import os
import sys
import io

import yaml

import schema205.md.schema_table as schema_table

def string_out_tables(instance, checkmark=None):
  struct = schema_table.load_structure_from_object(instance, checkmark=checkmark)
  output = None
  with io.StringIO() as output_file:
    # Data Types
    if len(struct['data_types']) > 0:
      output_file.writelines(schema_table.write_header("Data Types"))
      output_file.writelines(schema_table.data_types_table(struct['data_types']))
    # String Types
    if len(struct['string_types']) > 0:
      output_file.writelines(schema_table.write_header("String Types"))
      output_file.writelines(schema_table.string_types_table(struct['string_types']))
    # Enumerations
    if len(struct['enumerations']) > 0:
      for enum, enumerators in struct['enumerations'].items():
        output_file.writelines(schema_table.write_header(enum))
        output_file.writelines(schema_table.enumerators_table(enumerators))
    # Data Groups
    if len(struct['data_groups']) > 0:
      for dg, data_elements in struct['data_groups'].items():
        output_file.writelines(schema_table.write_header(dg))
        output_file.writelines(schema_table.data_groups_table(data_elements))
    output = output_file.getvalue()
  return output

def write_tables(instance, output_path, append=True, checkmark=None):
  with open(output_path, 'a' if append else 'w', encoding="utf-8") as output_file:
    output_file.write(string_out_tables(instance, checkmark=checkmark))

def write_file(input_path, output_path, checkmark=None):
  with open(input_path, 'r') as input_file:
      instance = yaml.load(input_file, Loader=yaml.FullLoader)
  write_tables(instance, output_path,append=False, checkmark=checkmark)
  print(f'Markdown generation successful for {input_path}')

def write_dir(input_dir_path, output_dir_path, checkmark=None):
  for file_name in sorted(os.listdir(input_dir_path)):
    if '.schema.yaml' in file_name:
      file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
      with open(os.path.join(input_dir_path,file_name), 'r') as input_file:
          instance = yaml.load(input_file, Loader=yaml.FullLoader)
      write_tables(instance, os.path.join(output_dir_path,f'{file_name_root}.schema.md'), append=False, checkmark=checkmark)
      print(f'Markdown generation successful for {file_name}')

if __name__ == '__main__':
  source_dir_path = os.path.join(os.path.dirname(__file__),'..','schema-source')
  build_dir_path = os.path.join(os.path.dirname(__file__),'..','build')
  if not os.path.exists(build_dir_path):
    os.mkdir(build_dir_path)
  docs_dir_path = os.path.join(build_dir_path,'docs')
  if not os.path.exists(docs_dir_path):
    os.mkdir(docs_dir_path)
  if len(sys.argv) == 2:
    write_file(os.path.join(source_dir_path,f'{sys.argv[1]}.schema.yaml'), os.path.join(docs_dir_path,f'{sys.argv[1]}.schema.md'))
  elif len(sys.argv) == 1:
    write_dir(source_dir_path, docs_dir_path)
