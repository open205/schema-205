import schema205.validate
import schema205.markdown
import schema205.json_translate
import schema205.cpp_translate
import schema205.render_template
import os
from doit.tools import create_folder

BUILD_PATH = os.path.join(os.path.dirname(__file__), 'build')
SOURCE_PATH = os.path.join(os.path.dirname(__file__), 'schema-source')
DOCS_PATH = os.path.join(BUILD_PATH,"docs")
SCHEMA_PATH = os.path.join(BUILD_PATH,"schema")
HEADER_PATH = os.path.join(BUILD_PATH, "include")
CPP_PATH = os.path.join(BUILD_PATH, "cpp")
RENDERED_TEMPLATE_PATH = os.path.realpath(
        os.path.join(BUILD_PATH,"rendered_template"))

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

def collect_lib_target_files(target_dir, extension):
  file_list = [os.path.join(target_dir,'libtk205.h'), 
               os.path.join(target_dir,'libtk205.cpp')]
  for file_name in sorted(os.listdir('schema-source')):
    if '.schema.yaml' in file_name:
      file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
      file_list.append(os.path.join(target_dir,f'{file_name_root}.{extension}'))
      #file_list.append(os.path.join(target_dir,f'{file_name_root}_factory.{extension}'))
  return file_list

def task_validate():
  '''Validates source-schema against meta-schema'''
  return {
    'file_dep': [os.path.join("meta-schema","meta.schema.json")] + collect_source_files(),
    'actions': [(schema205.validate.validate_dir,[SOURCE_PATH])]
  }

def task_doc():
  '''Generates Markdown tables from source-schema'''
  return {
    'file_dep': collect_source_files() + [
        os.path.join('schema205','markdown.py'),
        os.path.join('schema205','md','__init__.py'),
        os.path.join('schema205','md','schema_table.py'),
        os.path.join('schema205','md','grid_table.py'),
        ],
    'targets': collect_target_files(DOCS_PATH,'md'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [DOCS_PATH]),
      (schema205.markdown.write_dir,[SOURCE_PATH, DOCS_PATH])
      ],
    'clean': True
  }

def task_render_template():
  '''
  Demonstrate how to render a template
  '''
  template_dir = os.path.realpath(
          os.path.join('rendering_examples', 'template_rendering'))
  out_file = os.path.join(RENDERED_TEMPLATE_PATH, 'main.md')
  log_file = os.path.join(RENDERED_TEMPLATE_PATH, 'error-log.txt')
  return {
          'file_dep': collect_source_files() + [
              os.path.join(template_dir, 'main.md.j2'),
              os.path.join('schema205', 'markdown.py'),
              os.path.join('schema205', 'md', '__init__.py'),
              os.path.join('schema205', 'md', 'schema_table.py'),
              os.path.join('schema205', 'md', 'grid_table.py'),
              os.path.join('schema205', 'render_template.py'),
              ],
          'targets': [out_file, log_file],
          'task_dep': ['validate'],
          'actions': [
              (create_folder, [RENDERED_TEMPLATE_PATH]),
              (schema205.render_template.main,
                  ['main.md.j2', out_file, template_dir],
                  {"log_file": log_file})],
          'clean': True,
          }

def task_schema():
  '''Generates JSON schema from source-schema'''
  return {
    'file_dep': [os.path.join('schema205', 'json_translate.py')] + collect_source_files(),
    'targets': collect_target_files(SCHEMA_PATH,'json'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [SCHEMA_PATH]),
      (schema205.json_translate.translate_dir,[SOURCE_PATH, SCHEMA_PATH])
      ],
    'clean': True
  }

def task_cpp():
  '''Generates CPP source files from common-schema'''
  return {
    'file_dep': collect_source_files(),
    'targets': collect_lib_target_files(HEADER_PATH,'h') + collect_lib_target_files(CPP_PATH,'cpp'),
    'task_dep': ['validate'],
    'actions': [
      (create_folder, [HEADER_PATH]),
      (create_folder, [CPP_PATH]),
      (schema205.cpp_translate.translate_all_to_source,[SOURCE_PATH, HEADER_PATH, CPP_PATH, "ASHRAE205"])
      ],
    'clean': True
  }

def task_test():
  '''Performs unit tests and example file validation tests'''
  return {
    'task_dep': ['schema'],
    'actions': ['pytest -v test']
  }
