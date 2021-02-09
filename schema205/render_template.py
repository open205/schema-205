"""
Functionality to render Jinja templates with an add_table hook to generate
schema tables in Markdown.
"""
import re
import os
import traceback
try:
    import importlib.resources as pkg_resources
except ImportError:
    # use the backported 'importlib_resources' for python_version<3.7
    import importlib_resources as pkg_resources

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
import yaml

import schema205.md.schema_table as schema_table
import schema205.markdown as markdown
import schema205.schema_source as schema_source


def make_args_string(args_dict):
    """
    - args_dict: dict, the dictionary of local variable to value such as returned by locals()
    RETURN: string, all arguments in a string
    """
    return ", ".join(
            [f"{k}={repr(v)}" for k, v in reversed(list(args_dict.items()))])


def log_error(error, log):
    """
    - error: string
    - log: None or list of string
    RETURN: error string
    """
    if log is not None:
        log.append(error)
    return error


def make_error_string(msg, args_str):
    """
    - msg: string, an error message
    - args_str: string, original arguments
    RETURN: string, an error message
    """
    return ("\n---\nERROR\n" + msg +
            f"\nin call to `add_table({args_str})`\n---\n")


def render_header(level_and_content):
    """
    - level_and_content: None OR string OR list of [postive-int, string] OR tuple of
      (positive-int, string), the header level and content
    RETURN: string, the header
    """
    if level_and_content is None:
        return ""
    if isinstance(level_and_content, str):
        level = 1
        content = level_and_content
    elif isinstance(level_and_content, (list, tuple)):
        level, content = level_and_content
        if level < 1:
            level = 1
    else:
        raise Exception("Unhandle type of level_and_content")
    return "#" * level + " " + content + "\n\n"


def canonicalize_string(name):
    """
    Turns any string into a lowercase underscore single word
    - name: string, the table name
    RETURN: string, the name in canonical format
    """
    return "_".join([
        item.lower().strip()
        for item in re.split('\\s+', name.strip())])


def fetch_key_canonically(the_dict, canonical_key, default=None):
    """
    - the_dict: dictionary
    - canonical_key: any, the key of the dictionary
    - default: None or any, defaults to None. Returned if a canonical key match
      isn't found
    """
    for key, val in the_dict.items():
        if canonicalize_string(key) == canonical_key:
            return val
    return default


def extract_target_data(struct, table_name):
    """
    - struct: dict, raw data to pull from
    - table_name: string, assumed to be 'canonicalized' (via canonicalize_string)
    RETURN: Tuple of (None or string, None or dict or array, None or string for table type),
        - If there is an error, it is passed back as the first item; else None
        - If there is no error, the target data is passed back; else None if an error
        - If there is no error, we pass back the table type
    """
    if table_name in {'data_types', 'string_types'}:
        return (None, struct[table_name], table_name)
    for tbl in ['enumerations', 'data_groups']:
        table_type = tbl
        target = fetch_key_canonically(struct[tbl], table_name)
        if target is not None:
            break
    if target is None:
        return (
                f"`table_name` \"{table_name}\" was not `data_types` or `string_types`\n" +
                "and did not match any enumerators or data_groups in file!\n" +
                f"Possible enumerators: {', '.join(struct['enumerations'].keys())}\n" +
                f"Possible data_groups: {', '.join(struct['data_groups'].keys())}",
                None,
                None)
    return (None, target, table_type)


def determine_schema_dir(schema_dir):
    """
    - schema_dir: None or path-like, the path to the schema directory
    RETURN: path-like, the realized path
    """
    if schema_dir is None:
        # determine default path to package resources
        schema_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'schema-source')
    return schema_dir


def load_yaml_source(schema_dir, source, args_str):
    """
    - schema_dir: pathlike or None, the path to the schema directory. If None,
      use the packaged yaml files
    - source: string, the source key. E.g., for
      schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
    - args_str: string, the arguments to the calling function (for error
      reporting)
    RETURN: (string or None, None or dict), tuple of the error string if didn't
            load or the data to return
    """
    if schema_dir is None:
        try:
            data = pkg_resources.read_text(schema_source, source + '.schema.yaml')
        except FileNotFoundError as e:
            return (
                    make_error_string(
                        f"Schema source \"{source}\" from package " +
                        f"(\"{source + '.schema.yaml'}\") doesn't exist!",
                        args_str),
                    None)
        return (None, yaml.load(data, Loader=yaml.FullLoader))
    src_path = os.path.join(schema_dir, source + '.schema.yaml')
    if not os.path.exists(src_path):
        return (
                make_error_string(
                    f"Schema source \"{source}\" (\"{src_path}\") doesn't exist!",
                    args_str),
                None)
    with open(src_path, encoding='utf-8', mode='r') as input_file:
        data = yaml.load(input_file, Loader=yaml.FullLoader)
    return (None, data)


def make_add_table(schema_dir=None, error_log=None):
    """
    - schema_dir: string or pathlike OR None, the path to the schema directory.
      If None, indicates to use the local packaged yaml schemas.
    - error_log: None or list, if a list, then errors will be appended to the
      log as well as rendered into the final product
    RETURN: returns the add_table function with the following characteristics:
        - source: string, the source key. E.g., for
          schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
        - table_name: one of `data_types`, `string_types`, or a specific item
          from `enumerations`, or `data_groups`
        - caption: None or string, the table caption if desired
        - header_level_and_content: None OR Tuple of (positive-int, string), the
          header level and header conent if desired
        RETURN: string, returns a string representation of the given table
    """
    def add_table(
            source,
            table_name,
            caption=None,
            header_level_and_content=None):
        args_str = make_args_string(locals())
        err, data = load_yaml_source(schema_dir, source, args_str)
        if err is not None:
            return log_error(err, error_log)
        struct = schema_table.load_structure_from_object(data)
        err, target, table_type = extract_target_data(
                struct,
                canonicalize_string(table_name))
        if err is not None:
            return log_error(
                    make_error_string(err, args_str),
                    error_log)
        table_type_to_fn = {
                'data_types': schema_table.data_types_table,
                'string_types': schema_table.string_types_table,
                'enumerations': schema_table.enumerators_table,
                'data_groups': schema_table.data_groups_table,
                }
        gen_table = table_type_to_fn.get(table_type, None)
        if gen_table is None:
            return log_error(
                    make_error_string(
                        f"Unhandled table type \"{table_name}\"!",
                        args_str),
                    error_log)
        return render_header(header_level_and_content) + gen_table(
                target,
                caption=caption,
                add_training_ws=False)
    return add_table


def make_add_data_model(schema_dir=None, error_log=None):
    """
    - schema_dir: string or pathlike OR None, the path to the schema directory.
      If None, indicates to use the local packaged yaml schemas.
    - error_log: None or list, if a list, then errors will be appended to the
      log as well as rendered into the final product
    RETURN: returns the add_data_model function with the following characteristics:
        - source: string, the source key. E.g., for
          schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
        RETURN: string, returns a string representation of the given data models
    """
    def add_data_model(source):
        args_str = make_args_string(locals())
        err, data = load_yaml_source(schema_dir, source, args_str)
        if err is not None:
            return log_error(err, error_log)
        return markdown.string_out_tables(data)
    return add_data_model


def main(main_template, output_path, template_dir, schema_dir=None, log_file=None):
    """
    - main_template: string, path to the main template file. Note: should be a
      path relative to template_dir, not a full path.
    - output_path: string, the output path to write the template to
    - template_dir: string, the directory where the templates (that
      main_template refers to) lives.
    - schema_dir: string, a custom path to the schema files (*.schema.yaml) to work from
    - log_file: string or None, if a string, the path to an error file to write
    RETURN: None
    SIDE-EFFECTS:
    - load the template main_template from template_dir
    - render that template
    - write the contents to output_path
    """
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
        comment_start_string="{##",
        comment_end_string="##}")
    errs = None # errors
    if log_file is not None:
        errs = []
    try:
        temp = env.get_template(main_template)
        with open(output_path, encoding='utf-8', mode='w') as handle:
            handle.write(
                    temp.render(
                        add_table=make_add_table(schema_dir, errs),
                        add_data_model=make_add_data_model(schema_dir, errs)))
    except TemplateNotFound as exc:
        print(f"Could not find main template {main_template}")
        print(f"main_template = {main_template}")
        print(f"output_path = {output_path}")
        print(f"template_dir = {template_dir}")
        print("Exception:")
        print(exc)
        traceback.print_exc()
    if log_file is not None:
        with open(log_file, 'w') as handle:
            if len(errs) > 0:
                for err in errs:
                    handle.write(err.strip())
                    handle.write("\n")
