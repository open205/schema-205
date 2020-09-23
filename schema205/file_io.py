import json
import yaml
import os

def load_json(input_file_path):
  with open(input_file_path, 'r') as input_file:
    return json.load(input_file)

def get_extension(file):
    return os.path.splitext(file)[1]


def load(input_file_path):
    ext = get_extension(input_file_path).lower()
    if (ext == '.json'):
        with open(input_file_path, 'r') as input_file:
            return json.load(input_file)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(input_file_path, 'r') as input_file:
            return yaml.load(input_file, Loader=yaml.FullLoader)
    else:
        raise Exception(f"Unsupported input \"{ext}\".")


def dump(content, output_file_path):
    ext = get_extension(output_file_path).lower()
    if (ext == '.json'):
        with open(output_file_path,'w') as output_file:
            json.dump(content, output_file, indent=4)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(output_file_path, 'w') as out_file:
            yaml.dump(content, out_file, sort_keys=False)
    elif ext == '.h':
        with open(output_file_path, 'w') as header:
            header.write(content)
            header.write('\n')

    else:
        raise Exception(f"Unsupported output \"{ext}\".")


