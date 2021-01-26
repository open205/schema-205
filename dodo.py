import schema205.validate
import schema205.markdown
import schema205.json_translate
import schema205.render_jinja
import os
from doit.tools import create_folder

BUILD_PATH = "build"
SOURCE_PATH = 'schema-source'
DOCS_PATH = os.path.join(BUILD_PATH,"docs")
SCHEMA_PATH = os.path.join(BUILD_PATH,"schema")
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

def task_validate():
  '''Validates common-schema against meta-schema'''
  return {
    'file_dep': [os.path.join("meta-schema","meta.schema.json")] + collect_source_files(),
    'actions': [(schema205.validate.validate_dir,[SOURCE_PATH])]
  }

def task_doc():
  '''Generates Markdown tables from common-scema'''
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

def task_render_template():
  '''
  Demonstrate how to render a template using Jinja2 and the add_table hook.
  '''
  template_dir = os.path.realpath(
          os.path.join('rendering_examples', 'template_rendering'))
  return {
          'file_dep': collect_source_files() + [
              os.path.join(template_dir, 'main.md'),
              os.path.join('schema205', 'markdown.py'),
              os.path.join('schema205', 'schema_tables.py'),
              os.path.join('schema205', 'make_grid_table.py'),
              os.path.join('schema205', 'render_jinja.py'),
              ],
          'targets': [os.path.join(RENDERED_TEMPLATE_PATH, 'main.md')],
          'task_dep': ['validate'],
          'actions': [
              (create_folder, [RENDERED_TEMPLATE_PATH]),
              (schema205.render_jinja.main, [
                  'main.md',
                  os.path.join(RENDERED_TEMPLATE_PATH, 'main.md'),
                  template_dir,
                  ])],
          'clean': True,
          }

def task_schema():
  '''Generates JSON schema from common-scema'''
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

def task_test():
  '''Performs unit tests and example file validation tests'''
  return {
    'task_dep': ['schema'],
    'actions': ['pytest -v test']
  }
