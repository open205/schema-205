import csv
import yaml
import os

with open(os.path.join(os.path.dirname(__file__),'refrigerants.csv')) as csv_file:
  reader = csv.reader(csv_file)
  ref_dict = {'RefrigerantType': {'Object Type': "Enumeration", "Enumerators": {}}}
  for row, contents in enumerate(reader):
    if row == 0:
      continue
    else:
      ref_num = contents[0]
      ref_name = contents[1]
      ref_formula = contents[2]
      ref_family = contents[3]
      ref_enum = f"R{ref_num.upper().replace('(','').replace(')','')}"
      ref_notes = f"{ref_family} {ref_formula}" if len(ref_formula) > 0 else f"{ref_family}"
      ref_dict['RefrigerantType']["Enumerators"][ref_enum] = {"Description": ref_name, "Notes": ref_notes,"Display Text": f"R-{ref_num}"}

with open(os.path.join(os.path.dirname(__file__),'RefrigerantType.schema.yaml'), 'w') as out_file:
    yaml.dump(ref_dict, out_file, sort_keys=False)


