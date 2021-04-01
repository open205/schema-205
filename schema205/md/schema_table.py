"""
Specifics for setting up schema tables.
"""
from copy import deepcopy

import schema205.md.grid_table as grid_table


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
    for str_typ in string_types:
        new_item = deepcopy(str_typ)
        if 'Is Regex' in new_item and new_item['Is Regex']:
            new_item['JSON Schema Pattern'] = '(Not applicable)'
        new_item['JSON Schema Pattern'] = new_item['JSON Schema Pattern'].replace('*',r'\*').replace(r'(?','\n'r'(?').replace(r'-[','\n'r'-[')
        new_list.append(new_item)
    return new_list


def compress_notes(a_dict):
    """
    - a_dict: Dict, a dictionary that may contain the key, 'Notes"
    RETURN:
    None
    SIDE-EFFECTS:
    modifies d in place to replace the "Notes" value with a string if it is an
    array.
    """
    notes = "Notes"
    if notes in a_dict:
        if isinstance(a_dict[notes], list):
            a_dict[notes] = "\n\n".join([f"- {note}" for note in a_dict[notes]])


def data_elements_dict_from_data_groups(data_groups):
    """
    - data_groups: Dict, the data groups dictionary
    RETURN: Dict with data elements as an array
    """
    output = {}
    for dat_gr in data_groups:
        data_elements = []
        for element in data_groups[dat_gr]["Data Elements"]:
            new_obj = data_groups[dat_gr]["Data Elements"][element]
            new_obj["Name"] = f"`{element}`"
            if 'Required' in new_obj:
                if new_obj["Required"] == True:
                    check = u'\N{check mark}'
                    new_obj["Req"] = f"${check}$" if new_obj["Required"] else ''
                elif new_obj["Required"] == False:
                    new_obj["Req"] = ''
                else:
                    new_obj["Req"] = f"`{new_obj['Required']}`"
                new_obj.pop('Required')
            new_obj['Data Type'] = f"`{new_obj['Data Type']}`"
            if 'Constraints' in new_obj:
                gte = u'\N{GREATER-THAN OR EQUAL TO}'
                lte = u'\N{LESS-THAN OR EQUAL TO}'
                if type(new_obj["Constraints"]) is list:
                    new_obj["Constraints"] = ", ".join(new_obj["Constraints"])
                new_obj["Constraints"] = f"`{new_obj['Constraints'].replace('<=',lte).replace('>=',gte)}`"
            if 'Units' in new_obj:
                if new_obj['Units'] == '-':
                    new_obj['Units'] = '\\-'
            compress_notes(new_obj)
            data_elements.append(new_obj)
        output[dat_gr] = data_elements
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
            compress_notes(item)
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
    return (grid_table.string_out_table(data, columns, caption) +
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
    - caption: None or string, optional caption
    - add_training_ws: Bool, if True, adds trailing whitespace
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


def enumerators_table(enumerators, caption=None, add_training_ws=True):
    """
    - enumerators: array of ..., the enumerators array
    - caption: None or string, optional caption
    - add_training_ws: Bool, if True, adds trailing whitespace
    RETURN: string, the table in Pandoc markdown grid table format
    """
    return create_table_from_list(
            columns=["Enumerator", "Description", "Notes"],
            data_list=enumerators,
            caption=caption,
            add_training_ws=add_training_ws,
            defaults={"Notes": ""})


def data_groups_table(data_elements, caption=None, add_training_ws=True):
    """
    - data_elements: array of ..., the data elements
    - caption: None or string, optional caption
    - add_training_ws: Bool, if True, adds trailing whitespace
    RETURN: string, the table in Pandoc markdown grid table format
    """
    return create_table_from_list(
            columns=[
                "Name", "Description", "Data Type", "Units", "Constraints",
                "Req", "Notes"],
            data_list=data_elements,
            caption=caption,
            add_training_ws=add_training_ws,
            defaults={"Notes": "", "Req": "", "Units": "", "Constraints": ""})
