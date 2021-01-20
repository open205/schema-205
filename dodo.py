import schema205.validate
import schema205.markdown
import schema205.json_translate
import schema205.cpp_translate
import os
from doit.tools import create_folder

BUILD_PATH = "build"
SOURCE_PATH = 'schema-source'
DOCS_PATH = os.path.join(BUILD_PATH,"docs")
SCHEMA_PATH = os.path.join(BUILD_PATH,"schema")
HEADER_PATH = os.path.join(BUILD_PATH, "include")
CPP_PATH = os.path.join(BUILD_PATH, "cpp")

def collect_source_files():
  file_list = []
  for file_name in sorted(os.listdir('schema-source')):
    if '.schema.yaml' in file_name:
      file_list.append(os.path.join(SOURCE_PATH,file_name))
  return file_list

def collect_target_files(target_dir, extension):
  file_list = []
  for file_name in sorted(os.listdir('schema-source')):
    if '.schema.yaml' in file_name:
      file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
      file_list.append(os.path.join(target_dir,f'{file_name_root}.schema.{extension}'))
  return file_list

def task_validate():
  '''Validates common-schema against meta-schema'''
  return {
    'file_dep': [os.path.join("meta-schema","meta.schema.json")] + collect_source_files(),
    'actions': [(schema205.validate.validate_dir,[SOURCE_PATH])]
  }

def task_doc():
  '''Generates Markdown tables from common-schema'''
  return {
    'file_dep': collect_source_files() + [os.path.join('schema205','markdown.py')],
    'targets': collect_target_files(DOCS_PATH,'md'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [DOCS_PATH]),
      (schema205.markdown.write_dir,[SOURCE_PATH, DOCS_PATH])
      ],
    'clean': True
  }

def task_schema():
  '''Generates JSON schema from common-schema'''
  return {
    'file_dep': collect_source_files(),
    'targets': collect_target_files(SCHEMA_PATH,'json'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [SCHEMA_PATH]),
      (schema205.json_translate.translate_dir,[SOURCE_PATH, SCHEMA_PATH])
      ],
    'clean': True
  }

def task_headers():
  '''Generates CPP header files from common-schema'''
  return {
    'file_dep': collect_source_files(),
    'targets': collect_target_files(HEADER_PATH,'h'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [HEADER_PATH]),
      (schema205.cpp_translate.translate_all_to_headers,[SOURCE_PATH, HEADER_PATH, "rs_instance_base", "ASHRAE205"])
      ],
    'clean': True
  }

def task_cpp():
  '''Generates CPP source files from common-schema'''
  return {
    'file_dep': collect_source_files(),
    'targets': collect_target_files(CPP_PATH,'cpp'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [CPP_PATH]),
      (schema205.cpp_translate.translate_all_to_source,[SOURCE_PATH, CPP_PATH, "RS_instance_base", "ASHRAE205"])
      ],
    'clean': True
  }

def task_test():
  '''Performs unit tests and example file validation tests'''
  return {
    'task_dep': ['schema'],
    'actions': ['pytest -v test']
  }
