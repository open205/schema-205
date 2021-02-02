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
          new_obj["Enumerator"] = f"`{enumerator}`"
          if "Notes" in new_obj:
            if type(new_obj["Notes"]) is list:
              new_obj["Notes"] = "\n\n".join([f"- {note}" for note in new_obj["Notes"]])
          enumerators.append(new_obj)
        writer.value_matrix = enumerators

        output_file.writelines(format_table(writer))

    # Data Groups
    writer.headers = ["Name", "Description", "Data Type", "Units", "Range", "Req", "Notes"]
    if len(data_groups) > 0:
      for dg in data_groups:
        writer.table_name = dg
        data_elements = []
        for element in data_groups[dg]["Data Elements"]:
          new_obj = data_groups[dg]["Data Elements"][element]
          new_obj["Name"] = f"`{element}`"
          if 'Required' in new_obj:
            new_obj["Req"] = u'\N{check mark}' if new_obj["Required"] else ''
            new_obj.pop('Required')
          new_obj['Data Type'] = f"`{new_obj['Data Type']}`"
          if 'Range' in new_obj:
            gte = u'\N{GREATER-THAN OR EQUAL TO}'
            lte = u'\N{LESS-THAN OR EQUAL TO}'
            new_obj["Range"] = f"`{new_obj['Range'].replace('<=',lte).replace('>=',gte)}`"
          if "Notes" in new_obj:
            if type(new_obj["Notes"]) is list:
              new_obj["Notes"] = "\n\n".join([f"- {note}" for note in new_obj["Notes"]])
          data_elements.append(new_obj)
        writer.value_matrix = data_elements

        output_file.writelines(format_table(writer))

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