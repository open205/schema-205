import os
from pathlib import Path
from doit.tools import create_folder
from lattice import Lattice
from lattice.cpp.header_entry_extension_loader import load_extensions

DOIT_CONFIG = {'default_tasks': ['generate_meta_schemas', 'validate_schemas', 'generate_markdown']}

BUILD_PATH = Path(__file__).absolute().with_name("build")
create_folder(BUILD_PATH)
SOURCE_PATH = Path(__file__).absolute().parent

data_model_205 = Lattice(SOURCE_PATH, BUILD_PATH, build_output_directory_name=None, build_validation=False)

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

def task_generate_json_schemas():
    """Generate JSON schemas"""
    return {
        "task_dep": [f"validate_schemas"],
        "file_dep": [schema.file_path for schema in data_model_205.schemas]
        + [schema.meta_schema_path for schema in data_model_205.schemas],
        "targets": [schema.json_schema_path for schema in data_model_205.schemas],
        "actions": [(data_model_205.generate_json_schemas, [])],
        "clean": True,
    }

def task_validate_example_files():
    """Validate example files against JSON schema"""
    return {
        "file_dep": [schema.json_schema_path for schema in data_model_205.schemas]
        + data_model_205.examples,
        "task_dep": [f"generate_json_schemas"],
        "actions": [(data_model_205.validate_example_files, [])],
    }


def task_generate_markdown():
    """Generate markdown documentation from templates"""
    return {
        "targets": [template.markdown_output_path for template in data_model_205.doc_templates],
        "file_dep": [schema.file_path for schema in data_model_205.schemas]
        + [template.path for template in data_model_205.doc_templates],
        "task_dep": [f"validate_schemas"],
        "actions": [(data_model_205.generate_markdown_documents, [])],
        "clean": True,
    }


def task_generate_web_docs():
    """Generate markdown documentation from templates"""
    return {
        "task_dep": [f"validate_schemas", f"generate_json_schemas", f"validate_example_files"],
        "file_dep": [schema.file_path for schema in data_model_205.schemas]
        + [template.path for template in data_model_205.doc_templates],
        "targets": [Path(data_model_205.web_docs_directory_path, "public")],
        "actions": [(data_model_205.generate_web_documentation, [])],
        "clean": True,
    }


def task_generate_cpp_project():
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
#     """Run unit tests"""
#     return {"actions": ["pytest -v test"]}
