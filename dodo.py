import os
from pathlib import Path
import schema205.validate
import schema205.markdown
#import schema205.json_translate
#import schema205.cpp_translate
import schema205.render_template
from doit.tools import create_folder
from schema205.util import snake_style
from lattice import Lattice
from lattice.cpp.header_entry_extension_loader import load_extensions


BUILD_PATH = os.path.join(os.path.dirname(__file__), 'build')
create_folder(BUILD_PATH)
SOURCE_PATH = os.path.join(os.path.dirname(__file__), 'schema-source')
DOCS_PATH = os.path.join(BUILD_PATH,"docs")
SCHEMA_PATH = os.path.join(BUILD_PATH,"schema")
HEADER_PATH = os.path.join(BUILD_PATH, "include")
CPP_PATH = os.path.join(BUILD_PATH, "cpp")
RENDERED_TEMPLATE_PATH = os.path.realpath(
        os.path.join(BUILD_PATH,"rendered_template"))

data_model_205 = Lattice(SOURCE_PATH, BUILD_PATH, build_output_directory_name=None, build_validation=False)

def collect_target_files(target_dir, extension):
  file_list = []
  for file_name in sorted(os.listdir('schema-source')):
    if '.schema.yaml' in file_name:
      file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
      file_list.append(os.path.join(target_dir,f'{file_name_root}.schema.{extension}'))
  return file_list

def collect_lib_target_files(target_dir, extension):
  file_list = []
  for file_name in sorted(os.listdir('schema-source')):
    if '.schema.yaml' in file_name:
      file_name_root = snake_style(os.path.splitext(os.path.splitext(file_name)[0])[0])
      file_list.append(os.path.join(target_dir,f'{file_name_root}.{extension}'))
      file_list.append(os.path.join(target_dir,f'{file_name_root}_factory.{extension}'))
  return file_list


# def task_doc():
#   '''Generates Markdown tables from source-schema'''
#   return {
#     'file_dep': collect_source_files() + [
#         os.path.join('schema205','markdown.py'),
#         os.path.join('schema205','md','__init__.py'),
#         os.path.join('schema205','md','schema_table.py'),
#         os.path.join('schema205','md','grid_table.py'),
#         ],
#     'targets': collect_target_files(DOCS_PATH,'md'),
#     'task_dep': ['validate_schemas'],
#     'actions': [
#       (create_folder, [DOCS_PATH]),
#       (schema205.markdown.write_dir,[SOURCE_PATH, DOCS_PATH])
#       ],
#     'clean': True
#   }

# def task_render_template():
#   '''
#   Demonstrate how to render a template
#   '''
#   template_dir = os.path.realpath(
#           os.path.join('rendering_examples', 'template_rendering'))
#   out_file = os.path.join(RENDERED_TEMPLATE_PATH, 'main.md')
#   log_file = os.path.join(RENDERED_TEMPLATE_PATH, 'error-log.txt')
#   return {
#           'file_dep': collect_source_files() + [
#               os.path.join(template_dir, 'main.md.j2'),
#               os.path.join('schema205', 'markdown.py'),
#               os.path.join('schema205', 'md', '__init__.py'),
#               os.path.join('schema205', 'md', 'schema_table.py'),
#               os.path.join('schema205', 'md', 'grid_table.py'),
#               os.path.join('schema205', 'render_template.py'),
#               ],
#           'targets': [out_file, log_file],
#           'task_dep': ['validate_schemas'],
#           'actions': [
#               (create_folder, [RENDERED_TEMPLATE_PATH]),
#               (schema205.render_template.main,
#                   ['main.md.j2', out_file, template_dir],
#                   {"log_file": log_file})],
#           'clean': True,
#           }

def task_generate_meta_schemas():
  '''Generates JSON meta-schema from source-schema and meta.schema.yaml'''
  return {
    'file_dep': [schema.file_path for schema in data_model_205.schemas],
    'targets': [schema.meta_schema_path for schema in data_model_205.schemas],
    'actions': [
      (data_model_205.generate_meta_schemas,[])
      ],
    'clean': True
  }

def task_validate_schemas():
    """Validate the data model schemas against the JSON meta schema"""
    return {
      'file_dep': [schema.file_path for schema in data_model_205.schemas],
      'task_dep': ["generate_meta_schemas"],
      'actions': [(data_model_205.validate_schemas, [])]
    }

def task_cpp():
  '''Generates CPP source files from common-schema'''
  return {
    'file_dep': [schema.file_path for schema in data_model_205.schemas],
    'targets': [schema.cpp_header_file_path for schema in data_model_205.schemas]
                + [schema.cpp_source_file_path for schema in data_model_205.schemas]
                + data_model_205.cpp_support_headers,
    'task_dep': ['validate_schemas'],
    'actions': [
      (load_extensions, [Path(SOURCE_PATH, "cpp", "extensions")]),
      (data_model_205.generate_cpp_project, [])
      ],
    'clean': True
  }

# def task_test():
#   '''Performs unit tests and example file validation tests'''
#   return {
#     'task_dep': ['schema'],
#     'actions': ['pytest -v test']
#   }
