"""
Calls all Jinja templates to render a result.
"""
import os
import os.path
from copy import deepcopy

import schema205.make_grid_table as tables

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
SCHEMA_DIR = os.path.abspath(
    os.path.join(THIS_DIR, '..', 'schema-source'))


def write_header(heading, level=1):
    """
    - heading: string, the heading
    - level: integer, level > 0, the markdown level
    RETURN: string
    """
    return ("#"*level) + " " + heading + "\n\n"


def process_string_types(string_types):
    """
    - string_types: array of dict, the string types
    RETURN: list of dict, copy of string types list with regexes handled
    properly
    """
    new_list = []
    for st in string_types:
        new_item = deepcopy(st)
        if 'Is Regex' in new_item and new_item['Is Regex']:
            new_item['JSON Schema Pattern'] = '(Not applicable)'
        new_list.append(new_item)
    return new_list


def compress_notes(d):
    """
    - d: Dict, a dictionary that may contain the key, 'Notes"
    RETURN:
    None
    SIDE-EFFECTS:
    modifies d in place to replace the "Notes" value with a string if it is an array.
    """
    k = "Notes"
    if k in d:
        if type(d[k]) is list:
            d[k] = "\n\n".join([f"- {note}" for note in d[k]])


def data_elements_dict_from_data_groups(data_groups):
    """
    - data_groups: Dict, the data groups dictionary
    RETURN: Dict with data elements as an array
    """
    output = {}
    for dg in data_groups:
        data_elements = []
        for element in data_groups[dg]["Data Elements"]:
            new_obj = data_groups[dg]["Data Elements"][element]
            new_obj["Name"] = f"`{element}`"
            if 'Required' in new_obj:
                new_obj["Req"] = u'\N{check mark}' if new_obj["Required"] else ''
                new_obj.pop('Required')
            new_obj['Data Type'] = f"`{new_obj['Data Type']}`"
            if 'Range' in new_obj:
                gte = u'\N{GREATER-THAN OR EQUAL TO}'
                lte = u'\N{LESS-THAN OR EQUAL TO}'
                new_obj["Range"] = f"`{new_obj['Range'].replace('<=',lte).replace('>=',gte)}`"
            compress_notes(new_obj)
            data_elements.append(new_obj)
        output[dg] = data_elements
    return output


def enumerators_dict_from_enumerations(enumerations):
    """
    - enumerations: dict, the enumeration objects
    RETURN: list of dict, the enumeration objects as a list
    """
    output = {}
    for enum in enumerations:
        output[enum] = []
        for enumerator in enumerations[enum]["Enumerators"]:
            if enumerations[enum]["Enumerators"][enumerator]:
                item = deepcopy(enumerations[enum]["Enumerators"][enumerator])
            else:
                item = {}
            item["Enumerator"] = f"`{enumerator}`"
            output[enum].append(item)
    return output


def load_structure_from_object(instance):
    """
    - instance: dictionary, the result of loading a *.schema.yaml file
    RETURN: {
        'data_types': array,
        'string_types': array,
        'enumerations': dict,
        'data_groups': dict,
    }
    """
    data_types = []
    string_types = []
    enumerations = {}
    data_groups = {}

    for obj in instance:
        object_type = instance[obj]["Object Type"]
        if object_type == "Data Type":
            new_obj = instance[obj]
            new_obj["Data Type"] = f'`{obj}`'
            new_obj["Examples"] = ', '.join(new_obj["Examples"])
            data_types.append(new_obj)
        elif object_type == "String Type":
            new_obj = instance[obj]
            new_obj["String Type"] = f'`{obj}`'
            new_obj["Examples"] = ', '.join(new_obj["Examples"])
            string_types.append(new_obj)
        elif object_type == "Enumeration":
            new_obj = instance[obj]
            compress_notes(new_obj)
            enumerations[obj] = new_obj
        elif "Data Elements" in instance[obj]:
            data_groups[obj] = instance[obj]
        elif object_type == "Meta":
            pass
        else:
            print(f"Unknown object type: {object_type}.")
    return {
        'data_types': data_types,
        'string_types': process_string_types(string_types),
        'enumerations': enumerators_dict_from_enumerations(enumerations),
        'data_groups': data_elements_dict_from_data_groups(data_groups),
    }


def trailing_ws(flag):
    """
    - flag: bool, if True, return two newlines
    RETURN: string
    """
    return "\n\n" if flag else ""


def create_table_from_list(
        columns,
        data_list,
        defaults=None,
        caption=None,
        add_training_ws=True):
    """
    - columns: array of string, the column headers
    - data_list: array of dict with keys corresponding to columns array
    - defaults: None or dict from string to value, the defaults to use for a
      column if data missing
    - caption: None or string, if specified, adds a caption
    - add_training_ws: Bool, if True, adds trailing whitespace
    RETURN: string, the table in Pandoc markdown grid table format
    """
    if len(data_list) == 0:
        return ""
    data = {col:[] for col in columns}
    for col in columns:
        data[col] = []
        for item in data_list:
            if col in item:
                data[col].append(item[col])
            elif defaults is not None and col in defaults:
                data[col].append(defaults[col])
            else:
                raise Exception(f"Expected item to have key `{col}`: `{item}`")
    return (tables.string_out_table(data, columns, caption, None, None) +
            trailing_ws(add_training_ws))


def data_types_table(data_types, caption=None, add_training_ws=True):
    """
    - data_types: array of ..., the data types
    - caption: None or string, optional caption
    - add_training_ws: Bool, if True, adds trailing whitespace
    RETURN: string, the table in Pandoc markdown grid table format
    """
    return create_table_from_list(
            columns=[
                "Data Type", "Description", "JSON Schema Type", "Examples"],
            data_list=data_types,
            defaults=None,
            caption=caption,
            add_training_ws=add_training_ws)


def string_types_table(string_types, caption=None, add_training_ws=True):
    """
    - string_types: array of ..., the string types
    RETURN: string, the table in Pandoc markdown grid table format
    """
    return create_table_from_list(
            columns=[
                "String Type", "Description", "JSON Schema Pattern",
                "Examples"],
            data_list=string_types,
            caption=caption,
            add_training_ws=add_training_ws,
            defaults=None)


def enumerators_table(enumerators):
    """
    - enumerators: array of ..., the enumerators array
    RETURN: string, the table in Pandoc markdown grid table format
    """
    return create_table_from_list(
            columns=["Enumerator", "Description", "Notes"],
            data_list=enumerators,
            defaults={"Notes": ""})


def data_groups_table(data_elements):
    """
    - data_elements: array of ..., the data elements
    RETURN: string, the table in Pandoc markdown grid table format
    """
    return create_table_from_list(
            columns=[
                "Name", "Description", "Data Type", "Units", "Range",
                "Req", "Notes"],
            data_list=data_elements,
            defaults={"Notes": "", "Req": "", "Units": "", "Range": ""})


def get_base_stem(path):
    """
    - path: string, the path
    RETURN: string, the basename without extenstion
    """
    return os.path.splitext(os.path.basename(path))[0]


def make_data_type_table_spec(yaml_src, caption):
    """
    Creates a 'Table Secification' or table_spec
    - yaml_src: string, the source YAML file path
    - caption: string, the caption for the table
    RETURN: TableSpec
    """
    return {
        "yaml_source": yaml_src,
        "caption": caption,
        "select_by": {
            "data_path": ["Object Type"],
            "equals": "Data Type",
        },
        "columns": [
            {
                "data_path": [],
                "name_in_table": "Data Type",
            },
            {
                "data_path": ["Description"],
                "name_in_table": "Description",
            },
            {
                "data_path": ["JSON Schema Type"],
                "name_in_table": "JSON Schema Type",
            },
            {
                "data_path": ["Examples"],
                "name_in_table": "Examples",
                "transforms": [tables.join_with_comma],
            }
        ]
    }


def make_string_type_table_spec(yaml_src, caption):
    """
    Creates a 'Table Secification' or table_spec
    - yaml_src: string, the source YAML file path
    - caption: string, the caption for the table
    RETURN: TableSpec
    """
    return {
        "yaml_source": yaml_src,
        "caption": caption,
        "select_by": {
            "data_path": ["Object Type"],
            "equals": "String Type",
        },
        "columns": [
            {
                "data_path": [],
                "name_in_table": "Data Type",
            },
            {
                "data_path": ["Description"],
                "name_in_table": "Description",
            },
            {
                "data_path": ["JSON Schema Pattern"],
                "name_in_table": "JSON Schema Pattern",
                "default": "(Not applicable)",
                "transforms": [
                    tables.add_space_between("-", "["),
                    tables.add_space_between("]", "]"),
                    tables.add_space_between(")", ")"),
                    tables.add_space_between(")", "("),
                    tables.add_space_between(")", "\\."),
                    tables.add_space_between("*", "["),
                    tables.add_space_between("0", "|"),
                    tables.add_space_between("*", "|"),
                    tables.add_space_between("+", "("),
                    tables.add_space_between("?", "("),
                    tables.add_space_between("]", "["),
                    tables.add_space_between("|", "["),
                    tables.add_space_between("]", "|"),
                    tables.add_space_between("]", "{"),
                    tables.add_space_between("}", ":"),
                    tables.add_space_between("]", ":"),
                    tables.add_space_between(")", ":"),
                    tables.add_space_between(":", "["),
                    tables.add_space_between(":", "("),
                    tables.add_space_between(":", "{"),
                ],
            },
            {
                "data_path": ["Examples"],
                "name_in_table": "Examples",
                "transforms": [
                    tables.join_with_comma,
                ],
            }
        ]
    }


def make_enumerator_table_spec(ident, yaml_src, caption, columns, key=None):
    """
    Make an Enumerator TableSpec
    - ident: string, the id to select
    - yaml_src: string, the path to the YAML file
    - caption: string, the caption
    - columns: array of column specs
    - key: None or String or "Enumerators", the key to use to match on
    """
    if key is None:
        key = "Enumerators"
    def make_rows(_, obj):
        enumerators = obj[key]
        return [(k, enumerators[k]) for k in sorted(enumerators.keys())]
    return {
        "yaml_source": yaml_src,
        "caption": caption,
        "select_by": {
            "data_path": [],
            "equals": ident,
        },
        "derive_rows": make_rows,
        "columns": columns,
    }


def name_to_yaml_path(name):
    """
    - name: string, name of a schema file
    RETURN: string, path to YAML file
    """
    return os.path.join(SCHEMA_DIR, f'{name}.schema.yaml')


def add_table(
        schema_name,
        table_type,
        caption=None,
        preferred_column_widths=None,
        with_header=False):
    """
    A 'user-facing' table API.
    - schema_name: the base-name of the YAML spec file to reference. E.g., for
      "ASHRAE205.schema.yaml", schema_name is "ASHRAE205"
    - table_type: one of "Data Type", "String Type", "RS_ID", "ASHRAE205", ...
    - caption: string or None, the table caption
    - preferred_column_widths: None or array of integer, the (minimum) column
      widths to set per column
    - with_header: Bool, if True, creates a markdown header prior to the table
    RETURN: string, the grid table
    """
    yaml_src = name_to_yaml_path(schema_name)
    if not os.path.exists(yaml_src):
        raise Exception(
            f"Schema source '{yaml_src}' does not exist in '{SCHEMA_DIR}'")
    if table_type == "Data Type":
        return tables.generate_table_to_string(
            make_data_type_table_spec(yaml_src, caption),
            preferred_size=preferred_column_widths)
    if table_type == "String Type":
        return tables.generate_table_to_string(
            make_string_type_table_spec(yaml_src, caption),
            preferred_size=preferred_column_widths)
    if table_type == "RS_ID":
        return tables.generate_table_to_string(
            make_enumerator_table_spec(
                "RSID", yaml_src, caption, [
                    {
                        "data_path": [],
                        "name_in_table": "RS_ID",
                    },
                    {
                        "data_path": ["Description"],
                        "name_in_table": "Title",
                    },
                ]
            ),
            preferred_size=preferred_column_widths,
            header=table_type if with_header else None
        )
    if table_type == "ASHRAE205":
        return tables.generate_table_to_string(
            make_enumerator_table_spec(
                table_type, yaml_src, caption, [
                    {
                        "data_path": [],
                        "name_in_table": "Name",
                    },
                    {
                        "data_path": ["Description"],
                        "name_in_table": "Description",
                    },
                    {
                        "data_path": ["Data Type"],
                        "name_in_table": "Data Type",
                    },
                    {
                        "data_path": ["Required"],
                        "name_in_table": "Req",
                        "transforms": [
                            tables.bool_to_checkmark
                        ],
                        "default": False,
                        "escape": False,
                    },
                    {
                        "data_path": ["Notes"],
                        "name_in_table": "Notes",
                        "default": "",
                    },
                ],
                key="Data Elements",
            ),
            preferred_size=preferred_column_widths,
            header=table_type if with_header else None
        )
    return tables.generate_table_to_string(
        make_enumerator_table_spec(
            table_type, yaml_src, caption, [
                {
                    "data_path": [],
                    "name_in_table": "Enumerator",
                },
                {
                    "data_path": ["Description"],
                    "name_in_table": "Definition",
                },
            ]
        ),
        preferred_size=preferred_column_widths,
        header=table_type if with_header else None)


def add_data_model(*args):
    """
    Placeholder for a feature to add the entire data model.
    - args: list of any, the passed in arguments
    RETURN: string
    """
    return "add_data_model(" + (", ".join([str(a) for a in args])) + ")"
