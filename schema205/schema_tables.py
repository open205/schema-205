"""
Calls all Jinja templates to render a result.
"""
import os
import os.path

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
            enumerations[obj] = instance[obj]
        elif "Data Elements" in instance[obj]:
            data_groups[obj] = instance[obj]
        elif object_type == "Meta":
            pass
        else:
            print(f"Unknown object type: {object_type}.")
    return {
        'data_types': data_types,
        'string_types': string_types,
        'enumerations': enumerations,
        'data_groups': data_groups,
    }


def data_types_table(data_types):
    """
    - data_types: array of ..., the data types
    RETURN: string
    """
    if len(data_types) == 0:
        return ""
    columns = ["Data Type", "Description", "JSON Schema Type", "Examples"]
    data = {c:[] for c in columns}
    for col in columns:
        data[col] = [dt[col] for dt in data_types]
    return tables.string_out_table(data, columns, None, None, None) + "\n\n"


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
