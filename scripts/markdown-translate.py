import os
import yaml
from pytablewriter import MarkdownTableWriter

with open(os.path.join(os.path.dirname(__file__),'..','src','ASHRAE205.schema.yaml'), 'r') as input_file:
    instance = yaml.load(input_file, Loader=yaml.FullLoader)

data_types = []
string_types = []
enumerations = {}
data_groups = {}

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

writer = MarkdownTableWriter()
writer.margin = 1

# Data Types
writer.table_name = "Data Types"
writer.headers = ["Data Type", "Description", "JSON Schema Type", "Examples"]
writer.value_matrix = data_types

print(writer.dumps())

# String Types
writer.table_name = "String Types"
writer.headers = ["String Type", "Description", "JSON Schema Pattern", "Examples"]
for st in string_types:
  if 'Is Regex' in st:
    st['JSON Schema Pattern'] = '(Not applicable)' if st['Is Regex'] else st['JSON Schema Pattern']

writer.value_matrix = string_types

print(writer.dumps())

# Enumerations
for enum in enumerations:
  writer.table_name = enum
  writer.headers = ["Enumerator", "Description", "Notes"]
  enumerators = []
  for enumerator in enumerations[enum]["Enumerators"]:
    new_obj = enumerations[enum]["Enumerators"][enumerator] if enumerations[enum]["Enumerators"][enumerator] else {}
    new_obj["Enumerator"] = enumerator
    enumerators.append(new_obj)
  writer.value_matrix = enumerators

  print(writer.dumps())

# Data Groups
for dg in data_groups:
  writer.table_name = dg
  writer.headers = ["Data Element Name", "Description", "Data Type", "Units", "Range", "Req", "Notes"]
  data_elements = []
  for element in data_groups[dg]["Data Elements"]:
    new_obj = data_groups[dg]["Data Elements"][element]
    new_obj["Data Element Name"] = element
    if 'Required' in new_obj:
      new_obj["Req"] = u'\N{check mark}' if new_obj["Required"] else ''
      new_obj.pop('Required')
    data_elements.append(new_obj)
  writer.value_matrix = data_elements

  print(writer.dumps())
