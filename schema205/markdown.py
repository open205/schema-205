import os
import yaml
from pytablewriter import MarkdownTableWriter
import sys
from .schema_tables import data_types_table, string_types_table
from .schema_tables import enumerators_table, data_groups_table, write_header
from .schema_tables import data_elements_from_data_groups

def format_table(writer):
  return writer.dumps() + "\n"

def write_tables(instance, output_path, append=True):
  data_types = []
  string_types = []
  enumerations = {}
  data_groups = {}

  for obj in instance:
    object_type = instance[obj]["Object Type"]
    if object_type == "Data Type":
      new_obj = instance[obj]
      new_obj["Data Type"] = f'`{obj}`'
      new_obj["Examples"] = ', '.join(new_obj["Examples"])
      data_types.append(new_obj)
    elif object_type == "String Type":
      new_obj = instance[obj]
      new_obj["String Type"] = f'`{obj}`'
      new_obj["Examples"] = ', '.join(new_obj["Examples"])
      string_types.append(new_obj)
    elif object_type == "Enumeration":
      enumerations[obj] = instance[obj]
    elif "Data Elements" in instance[obj]:
      data_groups[obj] = instance[obj]
    elif object_type == "Meta":
      None
    else:
      print(f"Unknown object type: {object_type}.")

  writer = MarkdownTableWriter()
  writer.margin = 1

  with open(output_path, 'a' if append else 'w', encoding="utf-8") as output_file:

    # Data Types
    if len(data_types) > 0:
      output_file.writelines(write_header("Data Types"))
      output_file.writelines(data_types_table(data_types))

    # String Types
    if len(string_types) > 0:
      output_file.writelines(write_header("String Types"))
      for st in string_types:
        if 'Is Regex' in st and st['Is Regex']:
          st['JSON Schema Pattern'] = '(Not applicable)'
      output_file.writelines(string_types_table(string_types))

    # Enumerations
    if len(enumerations) > 0:
      for enum in enumerations:
        output_file.writelines(write_header(enum))
        enumerators = []
        for enumerator in enumerations[enum]["Enumerators"]:
          new_obj = enumerations[enum]["Enumerators"][enumerator] if enumerations[enum]["Enumerators"][enumerator] else {}
          new_obj["Enumerator"] = f"`{enumerator}`"
          enumerators.append(new_obj)
        output_file.writelines(enumerators_table(enumerators))

    # Data Groups
    if len(data_groups) > 0:
      dgs = data_elements_from_data_groups(data_groups)
      for dg in dgs:
        output_file.writelines(write_header(dg))
        output_file.writelines(data_groups_table(dgs[dg]))

def write_file(input_path, output_path):
  with open(input_path, 'r') as input_file:
      instance = yaml.load(input_file, Loader=yaml.FullLoader)
  write_tables(instance, output_path,append=False)
  print(f'Markdown generation successful for {input_path}')

def write_dir(input_dir_path, output_dir_path):
  for file_name in sorted(os.listdir(input_dir_path)):
    if '.schema.yaml' in file_name:
      file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
      with open(os.path.join(input_dir_path,file_name), 'r') as input_file:
          instance = yaml.load(input_file, Loader=yaml.FullLoader)
      write_tables(instance, os.path.join(output_dir_path,f'{file_name_root}.schema.md'), append=False)
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
