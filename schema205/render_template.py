"""
Functionality to render Jinja templates with an add_schema_table hook to generate
schema tables in Markdown.
"""

import re
import os
import traceback

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
import yaml

import schema205.md.schema_table as schema_table
import schema205.md.grid_table as grid_table
import schema205.markdown as markdown


def make_args_string(args_dict):
    """
    - args_dict: dict, the dictionary of local variable to value such as returned by locals()
    RETURN: string, all arguments in a string
    """
    return ", ".join([f"{k}={repr(v)}" for k, v in reversed(list(args_dict.items()))])


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
    return (
        "\n---\nERROR\n" + msg + f"\nin call to `add_schema_table({args_str})`\n---\n"
    )


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
    return "_".join([item.lower().strip() for item in re.split("\\s+", name.strip())])


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
    if table_name in {"data_types", "string_types"}:
        return (None, struct[table_name], table_name)
    for tbl in ["enumerations", "data_groups"]:
        table_type = tbl
        target = fetch_key_canonically(struct[tbl], table_name)
        if target is not None:
            break
    if target is None:
        return (
            f'`table_name` "{table_name}" was not `data_types` or `string_types`\n'
            + "and did not match any enumerators or data_groups in file!\n"
            + f"Possible enumerators: {', '.join(struct['enumerations'].keys())}\n"
            + f"Possible data_groups: {', '.join(struct['data_groups'].keys())}",
            None,
            None,
        )
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
            "schema-source",
        )
    return schema_dir


def load_yaml_source(schema_dir, source, args_str):
    """
    - schema_dir: pathlike, the path to the schema directory
    - source: string, the source key. E.g., for
      schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
    - args_str: string, the arguments to the calling function (for error
      reporting)
    RETURN: (string or None, None or dict), tuple of the error string if didn't
            load or the data to return
    """
    src_path = os.path.join(schema_dir, source + ".schema.yaml")
    if not os.path.exists(src_path):
        return (
            make_error_string(
                f'Schema source "{source}" ("{src_path}") doesn\'t exist!', args_str
            ),
            None,
        )
    with open(src_path, encoding="utf-8", mode="r") as input_file:
        data = yaml.load(input_file, Loader=yaml.FullLoader)
    return (None, data)


def make_add_schema_table(schema_dir=None, error_log=None):
    """
    - schema_dir: string or pathlike, the path to the schema directory.
    - error_log: None or list, if a list, then errors will be appended to the
      log as well as rendered into the final product
    RETURN: returns the add_schema_table function with the following characteristics:
        - source: string, the source key. E.g., for
          schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
        - table_name: one of `data_types`, `string_types`, or a specific item
          from `enumerations`, or `data_groups`
        - caption: None or string, the table caption if desired
        - header_level_and_content: None OR Tuple of (positive-int, string), the
          header level and header content if desired
        RETURN: string, returns a string representation of the given table
    """
    schema_dir = determine_schema_dir(schema_dir)

    def add_schema_table(
        source, table_name, description=None, level=1, style="2 Columns"
    ):
        args_str = make_args_string(locals())
        err, data = load_yaml_source(schema_dir, source, args_str)
        if err is not None:
            return log_error(err, error_log)
        return write_schema_table(
            data, table_name, description, level, style, error_log
        )

    return add_schema_table


def write_schema_table(
    table_dict, table_name, description=None, level=1, style="2 Columns", error_log=None
):
    if description is None:
        description = table_name
    struct = schema_table.load_structure_from_object(table_dict)
    err, target, table_type = extract_target_data(
        struct, canonicalize_string(table_name)
    )
    if err is not None:
        return log_error(err, error_log)
    columns = {
        "data_types": ["Data Type", "Description", "JSON Schema Type", "Examples"],
        "string_types": [
            "String Type",
            "Description",
            "JSON Schema Pattern",
            "Examples",
        ],
        "enumerations": ["Enumerator", "Description", "Notes"],
        "data_groups": [
            "Name",
            "Description",
            "Data Type",
            "Units",
            "Constraints",
            "Req",
            "Notes",
        ],
    }
    return schema_table.create_table_from_list(
        columns[table_type],
        target,
        description=description,
        level=level,
        style=style,
    )


def make_add_schema_table_from_string(error_log=None):
    def add_schema_table_from_string(
        yaml_string, table_name=None, description=None, level=1, style="2 Columns"
    ):
        data = yaml.safe_load(yaml_string)
        if table_name is None:
            table_name = [name for name in data][0]
        return write_schema_table(
            data, table_name, description, level, style, error_log
        )

    return add_schema_table_from_string


def make_add_yaml_table():
    """
    RETURN: returns the add_yaml_table function with the following characteristics:
        - content: string containing YAML syntax for Headers and Data.
        - caption: None or string, the table caption if desired
        RETURN: string, returns a string representation of the given table
    """

    def add_yaml_table(content, caption=None):
        table_data = yaml.load(content, Loader=yaml.FullLoader)
        columns = table_data["Headers"]
        data = {}
        for i, column in enumerate(columns):
            data[column] = []
            for row in table_data["Data"]:
                data[column].append(row[i])
        return grid_table.string_out_table(data, columns, caption)

    return add_yaml_table


def make_add_data_model(schema_dir, error_log):
    """
    - schema_dir: string or pathlike, the path to the schema directory.
    - error_log: None or list, if a list, then errors will be appended to the
      log as well as rendered into the final product
    RETURN: returns the add_data_model function with the following characteristics:
        - source: string, the source key. E.g., for
          schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
        RETURN: string, returns a string representation of the given data models
    """
    schema_dir = determine_schema_dir(schema_dir)

    def add_data_model(source, base_level=1, style="2 Columns"):
        args_str = make_args_string(locals())
        err, data = load_yaml_source(schema_dir, source, args_str)
        if err is not None:
            return log_error(err, error_log)
        return markdown.string_out_tables(data, base_level, style=style)

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
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
        comment_start_string="{##",
        comment_end_string="##}",
    )
    errs = None  # errors
    if log_file is not None:
        errs = []
    try:
        temp = env.get_template(main_template)
        with open(output_path, encoding="utf-8", mode="w") as handle:
            handle.write(
                temp.render(
                    add_schema_table=make_add_schema_table(schema_dir, errs),
                    add_yaml_table=make_add_yaml_table(),
                    add_data_model=make_add_data_model(schema_dir, errs),
                    add_schema_table_from_string=make_add_schema_table_from_string(),
                )
            )
    except TemplateNotFound as exc:
        print(f"Could not find main template {main_template}")
        print(f"main_template = {main_template}")
        print(f"output_path = {output_path}")
        print(f"template_dir = {template_dir}")
        print("Exception:")
        print(exc)
        traceback.print_exc()
    if log_file is not None:
        with open(log_file, "w") as handle:
            if len(errs) > 0:
                for err in errs:
                    handle.write(err.strip())
                    handle.write("\n")
