import json

def load_json(input_file_path):
  with open(input_file_path, 'r') as input_file:
    return json.load(input_file)
