import os
import json
import posixpath
import jsonschema
import yaml

schema_path = os.path.join(os.path.dirname(__file__),'..','meta-schema','meta.schema.json')

with open(schema_path) as meta_schema_file:
  uri_path = os.path.abspath(os.path.dirname(schema_path))
  if os.sep != posixpath.sep:
      uri_path = posixpath.sep + uri_path

  resolver = jsonschema.RefResolver(f'file://{uri_path}/', meta_schema_file)
  validator = jsonschema.Draft7Validator(json.load(meta_schema_file), resolver=resolver)

  with open(os.path.join(os.path.dirname(__file__),'..','src','ASHRAE205.schema.yaml'), 'r') as input_file:
      instance = yaml.load(input_file, Loader=yaml.FullLoader)

  errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
  if len(errors) == 0:
      print(f"Validation successful")
  else:
      messages = []
      for error in errors:
        messages.append(f"{error.message} ({'.'.join([str(x) for x in error.path])})")
      messages = [f"{i}. {message}" for i, message in enumerate(messages, start=1)]
      message_str = '\n  '.join(messages)
      raise Exception(f"Validation failed with {len(messages)} errors:\n  {message_str}")
