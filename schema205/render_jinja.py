"""
Calls all Jinja main_templates to render a result.
"""
import os
import os.path
import traceback

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
import yaml

import schema205.schema_tables as schema_tables


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
SCHEMA_DIR = os.path.realpath(
        os.path.join(THIS_DIR, '..', 'schema-source'))


def make_args_string(args_dict):
    """
    - args_dict: dict, the dictionary of local variable to value such as returned by locals()
    RETURN: string, all arguments in a string
    """
    return ", ".join(
            [f"{k}={repr(v)}" for k, v in reversed(list(args_dict.items()))])


def make_error_string(msg, args_str):
    """
    - msg: string, an error message
    - args_str: string, original arguments
    RETURN: string, an error message
    """
    return ("\n---\n" +
            "ERROR\n" + msg + f"\nin call to `add_table({args_str})`\n---\n")


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


def extract_target_data(struct, table_type, item_type, args_str):
    """
    - struct: dict, raw data to pull from
    - table_type: string, assumed to be in lower case
    - item_type: string or None, if string, assumed to be in lower case
    - args_str: string, arguments string for reporting errors
    RETURN: Tuple of (None or string, None or dict or array),
        - If there is an error, it is passed back as the first item; else None
        - If there is no error, the target data is passed back; else None if an error
    """
    target = None
    if table_type == 'enumerations':
        if item_type is None:
            return (
                    make_error_string(
                        "Table type is \"enumerators\" but no `item_type` specified!",
                        args_str),
                    None)
        potentials = []
        found = False
        for enum, enumerators in struct['enumerations'].items():
            potentials.append(enum)
            if enum.lower() == item_type:
                target = enumerators
                found = True
                break
        if not found:
            return (
                    make_error_string(
                        "`item_type` did not match any enumerators in file! " +
                        f"Possible enumerators: {', '.join(potentials)}",
                        args_str),
                    None)
    elif table_type == 'data_groups':
        if item_type is None:
            return (
                    make_error_string(
                        "Table type is \"data_groups\" but no `item_type` specified!",
                        args_str),
                    None)
        potentials = []
        found = False
        for dat_gr, data_elements in struct['data_groups'].items():
            potentials.append(dat_gr)
            if dat_gr.lower() == item_type:
                target = data_elements
                found = True
                break
        if not found:
            return (
                    make_error_string(
                        "`item_type` did not match any data groups in file! " +
                        f"Possible data groups: {', '.join(potentials)}",
                        args_str),
                    None)
    else:
        target = struct[table_type]
    return (None, target)


def add_table(
        source,
        table_type,
        item_type=None,
        caption=None,
        header_level_and_content=None):
    """
    - source: string, the source key. E.g., for schema-source/ASHRAE205.schema.yaml, 'ASHRAE205'
    - table_type: one of `data_types`, `string_types`, `enumerations`, or `data_groups`
    - item_type: None or a string if table_type is `enumerations` or `data_groups`; the item to pull
    - caption: None or string, the table caption if desired
    - header_level_and_content: None OR Tuple of (positive-int, string), the
      header level and header conent if desired
    RETURN: string, returns a string representation of the given table
    """
    args_str = make_args_string(locals())
    src_path = os.path.join(SCHEMA_DIR, source + '.schema.yaml')
    if not os.path.exists(src_path):
        return make_error_string(
                f"Schema source \"{source}\" (\"{src_path}\") doesn't exist!",
                args_str)
    with open(src_path, 'r') as input_file:
        data = yaml.load(input_file, Loader=yaml.FullLoader)
    table_type_to_fn = {
            'data_types': schema_tables.data_types_table,
            'string_types': schema_tables.string_types_table,
            'enumerations': schema_tables.enumerators_table,
            'data_groups': schema_tables.data_groups_table,
            }
    gen_table = table_type_to_fn.get(table_type.lower(), None)
    if gen_table is None:
        return make_error_string(
                f"Unhandled table type \"{table_type}\"!",
                args_str)
    struct = schema_tables.load_structure_from_object(data)
    err, target = extract_target_data(
            struct,
            table_type.lower(),
            item_type.lower() if item_type is not None else None,
            args_str)
    if err is not None:
        return err
    return render_header(header_level_and_content) + gen_table(
            target,
            caption=caption,
            add_training_ws=False)


def main(main_template, output_path, template_dir):
    """
    - main_template: string, path to the main template file. Note: should be a
      path relative to template_dir, not a full path.
    - output_path: string, the output path to write the template to
    - template_dir: string, the directory where the templates (that
      main_template refers to) lives.
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
    try:
        temp = env.get_template(main_template)
        with open(output_path, 'w') as handle:
            handle.write(temp.render(add_table=add_table))
    except TemplateNotFound as exc:
        print(f"Could not find main template {main_template}")
        print(f"main_template = {main_template}")
        print(f"output_path = {output_path}")
        print(f"template_dir = {template_dir}")
        print("Exception:")
        print(exc)
        traceback.print_exc()
