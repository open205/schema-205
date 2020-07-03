import os
import yaml
from pytablewriter import MarkdownTableWriter
import sys

def format_table(writer):
  return writer.dumps() + "\n"

def write_tables(instance, output_path, append=True):
  data_types = []
  string_types = []
  enumerations = {}
  data_groups = {}
  performance_maps = {}
  map_variables = {}

  for obj in instance:
    object_type = instance[obj]["Object Type"]
    if object_type == "Data Type":
      new_obj = instance[obj]
      new_obj["Data Type"] = obj
      new_obj["Examples"] = ', '.join(new_obj["Examples"])
      data_types.append(new_obj)
    elif object_type == "String Type":
      new_obj = instance[obj]
      new_obj["String Type"] = obj
      new_obj["Examples"] = ', '.join(new_obj["Examples"])
      string_types.append(new_obj)
    elif object_type == "Enumeration":
      enumerations[obj] = instance[obj]
    elif object_type == "Data Group":
      data_groups[obj] = instance[obj]
    elif object_type == "Performance Map":
      performance_maps[obj] = instance[obj]
    elif object_type == "Map Variables":
      map_variables[obj] = instance[obj]

  writer = MarkdownTableWriter()
  writer.margin = 1

  with open(output_path, 'a' if append else 'w', encoding="utf-8") as output_file:

    # Data Types
    if len(data_types) > 0:
      writer.table_name = "Data Types"
      writer.headers = ["Data Type", "Description", "JSON Schema Type", "Examples"]
      writer.value_matrix = data_types

      output_file.writelines(format_table(writer))

    # String Types
    if len(string_types) > 0:
      writer.table_name = "String Types"
      writer.headers = ["String Type", "Description", "JSON Schema Pattern", "Examples"]
      for st in string_types:
        if 'Is Regex' in st:
          st['JSON Schema Pattern'] = '(Not applicable)' if st['Is Regex'] else st['JSON Schema Pattern']

      writer.value_matrix = string_types

      output_file.writelines(format_table(writer))

    # Enumerations
    if len(enumerations) > 0:
      writer.headers = ["Enumerator", "Description", "Notes"]
      for enum in enumerations:
        writer.table_name = enum
        enumerators = []
        for enumerator in enumerations[enum]["Enumerators"]:
          new_obj = enumerations[enum]["Enumerators"][enumerator] if enumerations[enum]["Enumerators"][enumerator] else {}
          new_obj["Enumerator"] = enumerator
          enumerators.append(new_obj)
        writer.value_matrix = enumerators

        output_file.writelines(format_table(writer))

    # Data Groups
    writer.headers = ["Data Element Name", "Description", "Data Type", "Units", "Range", "Req", "Notes"]
    if len(data_types) > 0:
      for dg in data_groups:
        writer.table_name = dg
        data_elements = []
        for element in data_groups[dg]["Data Elements"]:
          new_obj = data_groups[dg]["Data Elements"][element]
          new_obj["Data Element Name"] = element
          if 'Required' in new_obj:
            new_obj["Req"] = u'\N{check mark}' if new_obj["Required"] else ''
            new_obj.pop('Required')
          data_elements.append(new_obj)
        writer.value_matrix = data_elements

        output_file.writelines(format_table(writer))

    # Performance Maps
    if len(performance_maps) > 0:
      for pm in performance_maps:
        writer.table_name = pm
        data_elements = []
        for element in performance_maps[pm]["Data Elements"]:
          new_obj = performance_maps[pm]["Data Elements"][element]
          new_obj["Data Element Name"] = element
          if 'Required' in new_obj:
            new_obj["Req"] = u'\N{check mark}' if new_obj["Required"] else ''
            new_obj.pop('Required')
          data_elements.append(new_obj)
        writer.value_matrix = data_elements

        output_file.writelines(format_table(writer))

    # Map Variables
    if len(map_variables) > 0:
      for mv in map_variables:
        writer.table_name = mv
        data_elements = []
        for element in map_variables[mv]["Data Elements"]:
          new_obj = map_variables[mv]["Data Elements"][element]
          new_obj["Data Element Name"] = element
          if 'Required' in new_obj:
            new_obj["Req"] = u'\N{check mark}' if new_obj["Required"] else ''
            new_obj.pop('Required')
          data_elements.append(new_obj)
        writer.value_matrix = data_elements

        output_file.writelines(format_table(writer))

if __name__ == '__main__':
  source_dir = os.path.join(os.path.dirname(__file__),'..','src')
  build_path = os.path.join(os.path.dirname(__file__),'..','build')
  if not os.path.exists(build_path):
    os.mkdir(build_path)
  docs_path = os.path.join(build_path,'docs')
  if not os.path.exists(docs_path):
    os.mkdir(docs_path)
  if len(sys.argv) == 2:
    with open(os.path.join(source_dir,f'{sys.argv[1]}.schema.yaml'), 'r') as input_file:
        instance = yaml.load(input_file, Loader=yaml.FullLoader)
    write_tables(instance, os.path.join(docs_path,f'{sys.argv[1]}.schema.md'),append=False)
  elif len(sys.argv) == 1:
    for file_name in os.listdir(source_dir):
      if '.schema.yaml' in file_name:
        file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
        with open(os.path.join(source_dir,file_name), 'r') as input_file:
            instance = yaml.load(input_file, Loader=yaml.FullLoader)
        write_tables(instance, os.path.join(docs_path,f'{file_name_root}.schema.md'),append=False)