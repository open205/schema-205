import json
import yaml
import os
from collections import OrderedDict
import re
import enum

def get_extension(file):
    return os.path.splitext(file)[1]


def load(input_file_path):
    ext = get_extension(input_file_path).lower()
    if (ext == '.json'):
        with open(input_file_path, 'r') as input_file:
            return json.load(input_file)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(input_file_path, 'r') as input_file:
            return yaml.load(input_file, Loader=yaml.FullLoader)
    else:
        raise Exception(f"Unsupported input \"{ext}\".")


def dump(content, output_file_path):
    ext = get_extension(output_file_path).lower()
    if (ext == '.json'):
        with open(output_file_path,'w') as output_file:
            json.dump(content, output_file, indent=4)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(output_file_path, 'w') as out_file:
            yaml.dump(content, out_file, sort_keys=False)
    elif ext == '.h':
        with open(output_file_path, 'w') as header:
            header.write(content)
            header.write('\n')

    else:
        raise Exception(f"Unsupported output \"{ext}\".")


def bubble_sort(obj_list):
    '''From https://stackabuse.com/sorting-algorithms-in-python/'''
    # We set swapped to True so the loop runs at least once
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(obj_list) - 1):
            #print('Checking if', obj_list[i+1]._name, 'is less than', obj_list[i]._name)
            if obj_list[i+1] < obj_list[i]:
                # Swap the elements
                #print('Swapping', obj_list[i]._name, obj_list[i+1]._name)
                obj_list[i], obj_list[i + 1] = obj_list[i + 1], obj_list[i]
                # Set the flag to True so we'll loop again
                swapped = True


def modified_insertion_sort(obj_list):
    '''From https://stackabuse.com/sorting-algorithms-in-python/#insertionsort'''
    print('Insertion sorting...')
    swapped = False
    # Start on the second element as we assume the first element is sorted
    for i in range(1, len(obj_list)):
        item_to_insert = obj_list[i]
        # And keep a reference of the index of the previous element
        j = i - 1
        # Move all items of the sorted segment forward if they are larger than
        # the item to insert
        while j >= 0 and any(obj > item_to_insert for obj in obj_list[0:j+1]):
            obj_list[j + 1] = obj_list[j]
            swapped = True
            j -= 1
        # Insert the item
        obj_list[j + 1] = item_to_insert
    return swapped


def iterative_insertion_sort(obj_list):
    while modified_insertion_sort(obj_list):
        pass



# -------------------------------------------------------------------------------------------------
class CPP_entry:

    def __init__(self, name, parent=None):
        self._type = 'class'
        self._name = name
        self._opener = '{'
        self._access_specifier = "public:"
        self._closure = '};'
        self._parent_entry = parent
        self._child_entries = list() # of CPP_entry(s)
        self._value = None

        if parent:
            self._lineage = parent._lineage + [name]
            self.parent.add_child_entry(self)
        else:
            self._lineage = [name]

    # def __eq__(self, other):
    #     return (self._name == other._name and
    #             self._type == other._type and
    #             self.lineage == other.lineage and
    #             self.child_entries == other.child_entries)

    # def __ne__(self, other):
    #     return not (self == other)

    def __lt__(self, other):
        '''Rich-comparison method to allow sorting.

           A CPP_entry must be "less than" any another CPP_entry that references it, i.e.
           you must define a value before you reference it.
        '''
        lt = self._less_than(other)
        print(self._name, 'lt', other._type + ' ' + other._name, '=', lt)
        return lt

    def _less_than(self, other):
        lt = False
        # if self._name in f'{other._type} {other._name}':
        #     return True
        for c in other.child_entries:
            t = f'{c._type} {c._name}'
            print('Comparing', self._name, '<', t)
            if self._name in t:
                print(self._name, 'less than', t)
                # Shortcut around checking siblings; if one child matches, then self < other
                return True
            else:
                # Check grandchildren
                lt = self._less_than(c)
        return lt

    def __gt__(self, other):
        return (other < self)

    def add_child_entry(self, child):
        self._child_entries.append(child)

    @property
    def value(self):
        entry = self.level*'\t' + self._type + ' ' + self._name + ' ' + self._opener + '\n'
        entry += (self.level + 1)*'\t' + self._access_specifier + '\n'
        for c in self._child_entries:
            entry += (c.value + '\n')
        entry += (self.level*'\t' + self._closure)
        return entry

    @property
    def child_entries(self):
        return self._child_entries

    @property
    def parent(self):
        return self._parent_entry

    @parent.setter
    def parent(self, p):
        self._parent_entry = p

    def _get_level(self, level=0):
        if self.parent:
            return self.parent._get_level(level+1)
        else:
            return level

    @property
    def level(self):
        return self._get_level()

    def _get_root(self):
        if self.parent:
            return self.parent._get_root()
        else:
            return self

    @property
    def rootname(self):
        return self._get_root()._name

    @property
    def lineage(self):
        return self._lineage


# -------------------------------------------------------------------------------------------------
class Typedef(CPP_entry):

    def __init__(self, name, parent, typedef):
        super().__init__(name, parent)
        self._type = 'typedef'
        self._access_specifier = ''
        self._typedef = typedef

    @property
    def value(self):
        return self.level*'\t' + self._type + ' ' + self._typedef + ' ' + self._name + ';'


# -------------------------------------------------------------------------------------------------
class Enumeration(CPP_entry):

    def __init__(self, name, parent, item_dict):
        super().__init__(name, parent)
        self._type = 'enum class'
        self._access_specifier = ''
        self._enumerants = list() # list of tuple:[value, description, display_text, notes]

        enums = item_dict
        for key in enums:
            descr = enums[key].get('Description')
            displ = enums[key].get('Display Text')
            notes = enums[key].get('Notes')
            # Currently, CPP only cares about the key (enum name)
            self._enumerants.append((key, descr, displ, notes))

    @property
    def value(self):
        z = list(zip(*self._enumerants))
        enums = z[0]
        entry = self.level*'\t' + self._type + ' ' + self._name + ' ' + self._opener + '\n'
        for e in enums:
            entry += (self.level + 1)*'\t'
            entry += (e + ',\n')
        entry += (self.level*'\t' + self._closure)
        return entry


# -------------------------------------------------------------------------------------------------
class Struct(CPP_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._type = 'struct'
        self._access_specifier = ''


# -------------------------------------------------------------------------------------------------
class Union(CPP_entry):

    def __init__(self, name, parent, selections):
        super().__init__(name, parent)
        self._type = 'union'
        self._access_specifier = ''
        self._selections = selections

    @property
    def value(self):
        entry = self.level*'\t' + self._type + ' ' + self._name + ' ' + self._opener + '\n'
        for s in self._selections:
            entry += (self.level + 1)*'\t'
            entry += (s + ';\n')
        entry += (self.level*'\t' + self._closure)
        return entry


# -------------------------------------------------------------------------------------------------
class Data_element(CPP_entry):

    def __init__(self, name, parent, element, data_types, references):
        super().__init__(name, parent)
        self._access_specifier = ''
        self._datatypes = data_types
        self._refs = references
        self._has_nested = False

        self._create_type_entry(element)

    @property
    def value(self):
        if self._has_nested:
            return super().value
        else:
            return self.level*'\t' + self._type + ' ' + self._name + ';'

    def _create_type_entry(self, parent_dict):
        '''Create type node.'''
        try:
            # If the type is an array, extract the surrounding [] first (using non-greedy qualifier "?")
            m = re.findall(r'\[(.*?)\]', parent_dict['Data Type'])
            if m:
                self._type = 'std::vector<' + self._get_simple_type(m[0]) + '>'
                # if 'Range' in parent_dict:
                #     self._get_simple_minmax(parent_dict['Range'])
            else:
                # If the type is oneOf a set
                m = re.findall(r'^\((.*)\)', parent_dict['Data Type'])
                if m:
                    choices = m[0].split(',')
                    self._type = 'union'
                    self._has_nested = True
                    for c in choices:
                        # Strip curly or other braces, convert PascalCase into underscore_case for
                        # element names
                        el_name = '_'.join(re.findall('([A-Z]+[0-9]*[a-z]*)', c)).lower()
                        # Create child elements of the union, in-situ
                        d = Data_element(el_name, self, {'Data Type' : c.strip()}, self._datatypes, self._refs)
                else:
                    # 1. 'type' entry
                    self._type = self._get_simple_type(parent_dict['Data Type'])
                    #self._get_simple_minmax(parent_dict['Range'])
        except KeyError as ke:
            #print('KeyError; no key exists called', ke)
            pass

    def _get_simple_type(self, type_str):
        ''' Return the internal type described by type_str.

            First, attempt to capture enum, definition, or special string type as references;
            then default to fundamental types with simple key "type".
        '''
        enum_or_def = r'(\{|\<)(.*)(\}|\>)'
        internal_type = None
        nested_type = None
        m = re.match(enum_or_def, type_str)
        if m:
            # Find the internal type. It might be inside nested-type syntax, but more likely
            # is a simple definition or enumeration.
            m_nested = re.match(r'.*?\((.*)\)', m.group(2))
            if m_nested:
                # Rare case of a nested specification e.g. 'ASHRAE205(RS_ID=RS0005)'
                internal_type = m.group(2).split('(')[0]
                nested_type = m_nested.group(1)
            else:
                internal_type = m.group(2)
        else:
            internal_type = type_str
        # Look through the references to assign a source to the type
        for key in self._refs:
            if internal_type in self._refs[key]:
                if key == self.rootname:
                    simple_type = internal_type
                else:
                    simple_type = key + '::' + internal_type
                if nested_type:
                    # Always in the form 'RS_ID=RSXXXX'
                    simple_type = nested_type.split('=')[1] + '*'
                return simple_type

        try:
            if '/' in type_str:
                # e.g. "Numeric/Null" 
                simple_type = self._datatypes[type_str.split('/')[0]]
            else:
                simple_type = self._datatypes[type_str]
        except KeyError:
            print('Type not processed:', type_str)
        return simple_type

    def _get_simple_minmax(self, range_str, target_dict):
        '''Process Range into min and max fields.'''
        if range_str is not None:
            ranges = range_str.split(',')
            minimum=None
            maximum=None
            if 'type' not in target_dict:
                target_dict['type'] = None
            for r in ranges:
                try:
                    numerical_value = re.findall(r'[+-]?\d*\.?\d+|\d+', r)[0]
                    if '>' in r:
                        minimum = (float(numerical_value) if 'number' in target_dict['type'] else int(numerical_value))
                        mn = 'exclusiveMinimum' if '=' not in r else 'minimum'
                        target_dict[mn] = minimum
                    elif '<' in r:
                        maximum = (float(numerical_value) if 'number' in target_dict['type']  else int(numerical_value))
                        mx = 'exclusiveMaximum' if '=' not in r else 'maximum'
                        target_dict[mx] = maximum
                except ValueError:
                    pass


# -------------------------------------------------------------------------------------------------
class H_translator:
    def __init__(self):
        self._references = dict()
        self._fundamental_data_types = dict()
        self._preamble = list()
        self._epilogue = list()

    def __str__(self):
        s = ''
        for p in self._preamble:
            s += p
        s += '\n'
        s += self._class.value
        s += '\n'
        for e in self._epilogue:
            s += e
        return s

    def load_schema(self, source_dir, input_rs):
        '''X'''
        self._input_rs = input_rs
        self._source_dir = source_dir
        self._references.clear()
        self._fundamental_data_types.clear()
        self._preamble.clear()
        self._epilogue.clear()

        input_file_path = os.path.join(source_dir, input_rs + '.schema.yaml')
        self._contents = load(input_file_path)
        # Load meta info first (assuming that base level tag == Schema means object type == Meta)
        self._load_meta_info(self._contents['Schema'])
        # Find the class description first, as it's stored at the same level as other data groups
        # but needs to be pushed to the top of the hierarchy
        self._add_include_guard(self._input_rs)
        self._add_included_headers(self._contents['Schema'].get('References'))
        self._class = CPP_entry(self._input_rs)
        # First, assemble typedefs
        for base_level_tag in [tag for tag in self._contents if self._contents[tag]['Object Type'] == 'String Type']:
            Typedef(base_level_tag, self._class, 'std::string')
        # Second, enumerations
        for base_level_tag in [tag for tag in self._contents if self._contents[tag]['Object Type'] == 'Enumeration']:
            Enumeration(base_level_tag, self._class, self._contents[base_level_tag]['Enumerators'])
        # Third, direct class member variables
        for data_element in self._contents[self._input_rs]['Data Elements']:
            Data_element(data_element, 
                         self._class, 
                         self._contents[self._input_rs]['Data Elements'][data_element],
                         self._fundamental_data_types,
                         self._references
                         )
        # Iterate through the dictionary, looking for known types
        for base_level_tag in self._contents:
            #if 'Object Type' in self._contents[base_level_tag]:
            obj_type = self._contents[base_level_tag].get('Object Type')
            if obj_type in ['Data Group',
                            'Performance Map',
                            'Grid Variables',
                            'Lookup Variables',
                            'Rating Data Group']:
                # Only collect data groups that aren't the class-level group
                if base_level_tag != self._input_rs:
                    s = Struct(base_level_tag, self._class)
                    for data_element in self._contents[base_level_tag]['Data Elements']:
                        Data_element(data_element, 
                                        s, 
                                        self._contents[base_level_tag]['Data Elements'][data_element],
                                        self._fundamental_data_types,
                                        self._references
                                        )
        modified_insertion_sort(self._class.child_entries)

    def _add_include_guard(self, header_name):
        s1 = f'#ifndef {header_name.upper()}_H_'
        s2 = f'#define {header_name.upper()}_H_'
        s3 = f'#endif'
        self._preamble.append(s1 + '\n' + s2 + '\n')
        self._epilogue.append(s3 + '\n')

    def _add_included_headers(self, ref_list):
        if ref_list:
            includes = ''
            for r in ref_list:
                includes += f'#include "{r}.h"'
                includes += '\n'
            self._preamble.append(includes)
        self._preamble.append('#include <string>\n#include <vector>\n')

    def _load_meta_info(self, schema_section):
        '''Store the global/common types and the types defined by any named references.'''
        refs = list()
        if 'References' in schema_section:
            refs = schema_section['References'].copy()
        refs.append(self._input_rs)
        for ref_file in refs:
            ext_dict = load(os.path.join(self._source_dir, ref_file + '.schema.yaml'))
            external_objects = list()
            for base_item in [name for name in ext_dict if ext_dict[name]['Object Type'] in (
                ['Enumeration',
                    'Data Group',
                    'String Type',
                    'Map Variables',
                    'Rating Data Group',
                    'Performance Map',
                    'Grid Variables',
                    'Lookup Variables'])]:
                external_objects.append(base_item)
            self._references[ref_file] = external_objects
            cpp_types = {'Integer' : 'int', 
                         'String' : 'std::string', 
                         'Numeric' : 'double', 
                         'Boolean': 'bool'}
            for base_item in [name for name in ext_dict if ext_dict[name]['Object Type'] == 'Data Type']:
                self._fundamental_data_types[base_item] = cpp_types.get(base_item)

    def _print_nodes(self, node):
        if not node.child_entries:
            print(node.lineage)
        for child in node.child_entries:
            self._print_nodes(child)


# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import glob

    h = H_translator()
    source_dir = os.path.join(os.path.dirname(__file__),'..','schema-source')
    build_dir = os.path.join(os.path.dirname(__file__),'..','build')
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    dump_dir = os.path.join(build_dir,'cpp')
    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)

    if len(sys.argv) == 2:
        file_name_root = sys.argv[1]
        h.load_schema(source_dir, file_name_root)
        dump(str(h), os.path.join(dump_dir, file_name_root + '.h'))
    else:
        yml = glob.glob(os.path.join(source_dir, '*.schema.yaml'))
        for file_name in yml:
            file_name_root = os.path.splitext(os.path.splitext(os.path.basename(file_name))[0])[0]
            h.load_schema(source_dir, file_name_root)
            dump(str(h), os.path.join(dump_dir, file_name_root + '.h'))


