"""
Markdown grid-table creation utilities
"""
import copy
import io
import traceback

import yaml


def wrap_text_to_lines(text, width, bold=False, left_space=1, right_space=1):
    """
    - text: string, the text to wrap
    - width: int, >0, the width to wrap to
    - bold: bool, if True, allow space for surrounding the beginning and end with **
    - left_space: int, >=0, the left space to enforce between cells
    - right_space: int, >=0, the right space to enforce between cells
    RETURN: (Array String), the lines
    """
    VERBOSE = False
    atoms = text.split(" ")
    if bold:
        atoms[0] = '**' + atoms[0]
        atoms[-1] = atoms[-1] + '**'
    longest_atom = max([len(s) for s in atoms])
    if longest_atom + left_space + right_space > width:
        print("Warning! Need to hyphenate atoms!")
    lines = []
    atom_idx = 0
    line_length = 0
    first = True
    line = ' '*left_space
    num_atoms = len(atoms)
    while atom_idx < num_atoms:
        if VERBOSE:
            print(f"atom_idx: {atom_idx}")
            print(f"line    : {line}")
            print(f"lines   : {lines}")
            print(f"atoms   : {atoms}")
        if first:
            new_line = line + atoms[atom_idx]
            first = False
        else:
            new_line = line + ' ' + atoms[atom_idx]
        if len(new_line) + right_space <= width:
            line = new_line
        else:
            lines.append(line + ' '*right_space)
            line = ' '*left_space + atoms[atom_idx]
        atom_idx += 1
    if len(line) > 0:
        lines.append(line + ' '*right_space)
    if VERBOSE:
        print(f"line    : {line}")
        print(f"lines   : {lines}")
        print(f"atoms   : {atoms}")
    return lines


def get_line_row(lines, row):
    """
    - lines: (Array string), array of lines
    - row: int, >=0, the row index to grab
    RETURN: string, if row greater than or equal to lines length, returns ''
    """
    if row < len(lines):
        return lines[row]
    return ''


def write_rule(sizes, is_header=False):
    """
    - sizes: (Array int), the column widths (of contents)
    RETURN: string
    """
    mark = '=' if is_header else '-'
    return '+' + ''.join([(mark*n + '+') for n in sizes]) + '\n'


def write_row(content, sizes, is_header=False):
    """
    RETURN: string
    """
    assert len(content) == len(sizes), 'len(content) must equal len(sizes)'
    table = write_rule(sizes) if is_header else ''
    list_of_lines = [
            wrap_text_to_lines(text=content[n], width=sizes[n], bold=is_header)
            for n in range(len(content))]
    for row_num in range(max([len(lines) for lines in list_of_lines])):
        table_line = '|' + ''.join(['{:' + str(n)  + 's}|' for n in sizes]) + '\n'
        texts = [get_line_row(lines, row_num) for lines in list_of_lines]
        table += table_line.format(*texts)
    table += write_rule(sizes, is_header=is_header)
    return table


def get_column_sizes(content, is_bold=False, has_spacing=True, preferred_sizes=None):
    """
    - content: (Array string), the column content
    - is_bold: Bool, True if the column content must be surrounded with '**'
    - has_spacing: Bool, True if we keep at least one space padding between cell border
    - preferred_sizes: None or (Array int), the preferred sizes of the columns.
      Will be at least this size
    RETURN: (Array int), the actual sizes
    """
    if preferred_sizes is None:
        sizes = [0] * len(content)
    else:
        sizes = copy.deepcopy(preferred_sizes)
    assert len(content) == len(sizes), "len(content) must equal len(sizes)"
    for col_num, col_name in enumerate(content):
        atoms = col_name.split(' ')
        longest_atom = max([len(s) for s in atoms])
        if is_bold:
            num_atoms = len(atoms)
            if num_atoms == 1:
                longest_atom += 4
            elif num_atoms > 1:
                longest_atom += 2
        if has_spacing:
            longest_atom += 2
        if longest_atom > sizes[col_num]:
            sizes[col_num] = longest_atom
    return sizes


def check_dict_of_arrays(doa, columns):
    """
    Checks the data-structure that dict of arrays has at least the keys in
    columns and that each entry's length is the same as the others.
    - doa: (Dict String (Array String)), dictionary with string keys to arrays of string
    - columns: (Array String), the columns of doa
    RETURN: (Array String), array of issues
    """
    issues = []
    length = None
    for c in columns:
        if c not in doa:
            issues.append(f"{c} not in doa")
            continue
        if length is None:
            try:
                length = len(doa[c])
            except:
                issues.append(f"could not take length of doa['{c}']")
        elif len(doa[c]) != length:
            issues.append(f"len(doa['{c}']) = {len(doa[c])} != {length}, the length of other columns")
    return issues


def assert_doa_valid(doa, columns):
    """
    Checks if DOA valid. If not, raises an exception.
    - doa: (Dict String (Array String)), dictionary with string keys to arrays of string
    - columns: (Array String), order of keys to write table out as
    """
    issues = check_dict_of_arrays(doa, columns)
    if len(issues) > 0:
        raise Exception("DictOfArraysInvalid: " + ";".join(issues))


def remove_blank_columns(doa, columns, sizes):
    """
    Remove columns that are blank. 
    - doa: (Dict String (Array String)), dictionary with string keys to arrays of string
    - columns: (Array String), order of keys to write table out as
    RETURN: (Tuple (Array String), (Array Integer)), tuple of new columns with
    blanks removed and new sizes
    """
    new_columns = []
    new_sizes = []
    for c, s in zip(columns, sizes):
        non_blanks = 0
        for row in doa[c]:
            if row is not None and row != "":
                non_blanks += 1
        if non_blanks > 0:
            new_columns.append(c)
            new_sizes.append(s)
    return new_columns, new_sizes


def make_table_from_dict_of_arrays(doa, columns, preferred_sizes=None, drop_blank_columns=True):
    """
    - doa: (Dict String (Array String)), dictionary with string keys to arrays of string
    - columns: (Array String), order of keys to write table out as
    - preferred_sizes: None or (Array Int) with preferred column sizes
    - drop_blank_columns: Bool, if True, drops columns where there are no
      entries for any rows in that columns
    RETURN: String, a grid table
    """
    if preferred_sizes is None:
        preferred_sizes = [0] * len(columns)
    if drop_blank_columns:
        columns, preferred_sizes = remove_blank_columns(doa, columns, preferred_sizes)
    assert_doa_valid(doa, columns)
    VERBOSE = True
    sizes = get_column_sizes(
            columns, is_bold=True, has_spacing=True,
            preferred_sizes=preferred_sizes)
    num_rows = len(doa[columns[0]])
    rows = []
    for row_num in range(num_rows):
        row = [doa[c][row_num] for c in columns]
        rows.append(row)
        sizes = get_column_sizes(
                row, is_bold=False, has_spacing=True, preferred_sizes=sizes)
    table = write_row(columns, sizes, True)
    for row in rows:
        table += write_row(row, sizes, False)
    return table


def string_out_table(d, columns, caption, preferred_sizes=None, table_size="footnotesize"):
    """
    - d: (Dict String (Array String)), dict of arrays of data for the table
    - columns: (Array String), the column names in desired order
    - path: string, path to where to save the table
    - caption: None or string
    - preferred_sizes: None or (Array Integer), the preferred column sizes; column will be at least that size
    - table_size: None or string, if string, one of "Huge", "huge", "LARGE", "Large", "large", "normalsize", "small", "footnotesize", "scriptsize", "tiny"
        the table size
    RETURN: string of the table in Markdown
    """
    if preferred_sizes is None:
        preferred_sizes = [0] * len(columns)
    s = ""
    with io.StringIO() as f:
        if table_size is not None:
            f.write(f"\\{table_size}\n\n")
        f.write(make_table_from_dict_of_arrays(
            d, columns=columns, preferred_sizes=preferred_sizes))
        if caption is not None:
            f.write(f"\nTable: {caption}\n")
        if table_size is not None:
            f.write("\n\\normalsize\n\n")
        s = f.getvalue()
    return s


def write_out_table(d, columns, path, caption, preferred_sizes=None, table_size="footnotesize"):
    """
    - d: (Dict String (Array String)), dict of arrays of data for the table
    - columns: (Array String), the column names in desired order
    - path: string, path to where to save the table
    - caption: None or string
    - preferred_sizes: None or (Array Integer), the preferred column sizes; column will be at least that size
    - table_size: None or string, if string, one of "Huge", "huge", "LARGE", "Large", "large", "normalsize", "small", "footnotesize", "scriptsize", "tiny"
        the table size
    RETURN: None
    SIDE_EFFECT: create table and write it to path as a pandoc grid table
    """
    with open(path, 'w') as f:
        f.write(string_out_table(d, columns, caption, preferred_sizes, table_size))


def get_data_path_from_obj(id, obj, path, default=None):
    """
    - id: string, the object id
    - obj: dict or list, an object or list
    - path: list of string or number, addresses the path into the object
    - default: (Or None string), if given, the default to return if path not found
    RETURN: data at the given path
    """
    v = id
    target = obj
    for p in path:
        try:
            v = target[p]
            target = v
        except:
            if default is None:
                raise Exception(f"failure to get id='{id}' from obj='{obj}' for path='{path}' at '{p}'")
            return default
    return v


def make_selector(select_by):
    if "data_path" in select_by and "equals" in select_by:
        def f(id, obj):
            v = get_data_path_from_obj(id, obj, select_by["data_path"])
            return v == select_by["equals"]
        return f
    raise Exception(f"Unhandled selector for {select_by}")


def join_with_comma(values):
    return ", ".join(values)


def add_space_between(left, right):
    def f(a_string):
        return a_string.replace(left + right, left + " " + right)
    return f


def bool_to_checkmark(a_bool):
    if str(a_bool).lower().strip() == 'true':
        return "\\Checkmark"
    return ""


def handle_transform(transform_type, value):
    if transform_type == "join_with_comma":
        return ", ".join(value)
    raise Exception(f"Unhandled transform for {transform_type} and {value}")


def make_preferred_sizes(columns, preferred_size=None):
    """
    - columns: (List {"preferred_size"?: PositiveInteger, ...})
    - preferred_size: (Or None (List PositiveInteger)), the preferred sizes
    RETURN: (Or None (List PositiveInteger))
    """
    if preferred_size is not None:
        return preferred_size
    derived_preferred_size = []
    for c in columns:
        if "preferred_size" in c:
            derived_preferred_size.append(c["preferred_size"])
        else:
            return None
    return derived_preferred_size


def escape_md(a_string):
    """
    - a_string, string, the source string
    RETURN: str, escaped to render correctly through Markdown
    """
    return a_string.replace("\\", "\\\\").replace("*", "\\*")


def generate_table_to_string(table_spec, preferred_size=None, header=None, header_level=3):
    """
    - table_spec: dict, a dictionary with keys to describe
        loading a table from YAML and writing it to Markdown
    RETURN: string    
    """
    with open(table_spec["yaml_source"]) as f:
        raw_data = yaml.load(f, Loader=yaml.CLoader)
    table_data = {c["name_in_table"]:[] for c in table_spec["columns"]}
    selector = make_selector(table_spec["select_by"])
    for k, v in raw_data.items():
        if selector(k, v):
            columns = []
            if "columns" in table_spec:
                columns = table_spec["columns"]
            elif "derive_columns" in table_spec:
                columns = table_spec["derive_columns"](k, v)
            if "derive_rows" in table_spec:
                rows = table_spec["derive_rows"](k, v)
            else:
                rows = [(k, v)]
            for row_k, row_v in rows:
                for c in columns:
                    col_src = get_data_path_from_obj(
                        row_k, row_v, c["data_path"], c.get("default", None))
                    if "transforms" in c:
                        for tx in c["transforms"]:
                            col_src = tx(col_src)
                    value = col_src
                    if c.get("escape", True):
                        value = escape_md(value)
                    table_data[c["name_in_table"]].append(value)
    columns = [c["name_in_table"] for c in table_spec["columns"]]
    try:
        s = string_out_table(
            table_data,
            columns,
            caption=table_spec["caption"],
            preferred_sizes=make_preferred_sizes(
                table_spec["columns"], preferred_size))
        if header is not None:
            s = ("#" * header_level) + " " + header + "\n\n" + s
        return s
    except Exception as e:
        print("Exception in trying to make table")
        print("table data: ", table_data)
        print("columns: ", columns)
        print("table_spec: ", table_spec)
        print(e)
        traceback.print_exc()


def generate_table(table_spec, preferred_size=None):
    """
    - table_spec: dict, a dictionary with keys to describe
        loading a table from YAML and writing it to Markdown
    RETURN: None
    EFFECTS:
    - write the given table from source YAML to Markdown
    """
    s = generate_table_to_string(table_spec, preferred_size)
    with open(table_spec["markdown_target"], 'w') as f:
        f.write(s)


if __name__ == "__main__":
    d = {
            'Name': [
                'manufacturer',
                'manufacturer_software_version',
                'model_number',
                'nominal_voltage',
                'nominal_frequency',
                'tolerance_standard',
                'compressor_type',
                'speed_control_type',
                'liquid_data_source',
                'refrigerant_type',
                'hotgas_bypass_installed',
                ],
            'Description': [
                'Manufacturer name',
                'Version of the software used to generate the performance map',
                'Model number',
                'Unit nominal voltage',
                'Unit nominal frequency',
                'Name and version of the testing or certification standard under which the chiller is rated',
                'Type of compressor',
                'Type of compressor speed control',
                'Source of the liquid properties data',
                'Refrigerant used in the chiller',
                'Indicates if a hot-gas bypass valve is installed on the chiller',
                ],
            'Data Type': [
                'String',
                'String',
                'Pattern',
                'Numeric',
                'Numeric',
                'String',
                '\\<CompressorType\\>',
                '\\<CompressorSpeedControlType\\>',
                'String',
                '\\<RefrigerantType\\>',
                'Boolean',
                ],
            'Units': [
                '',
                '',
                '',
                'V',
                'Hz',
                '',
                '',
                '',
                '',
                '',
                '',
                ],
            'Range': [
                '',
                '',
                '',
                '≥ 0',
                '≥ 0',
                '',
                '',
                '',
                '',
                '',
                '',
                ],
            'Req': [
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ],
            'Notes': [
                '',
                '',
                'Pattern shall match all model numbers that can be represented by the *representation*',
                'If the unit can operate at multiple voltages, the lower of the two shall be stated',
                'Power supply frequency for the intented region of installation',
                'Example: AHRI 550/590-2015, EN14511-2018, EN14825-2016, GB18430.1-2007',
                '',
                '',
                'Example: "ASHRAE Handbook Fundamentals 2013 chapter 31"',
                '',
                '',
                ],
            }
    print(
            make_table_from_dict_of_arrays(
                d,
                columns=['Name', 'Description', 'Data Type', 'Units', 'Range', 'Req', 'Notes'],
                preferred_sizes=[40] + [0]*6,
                ))
