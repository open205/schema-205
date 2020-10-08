import os
import re
from schema205.file_io import load

# -------------------------------------------------------------------------------------------------
class Header_entry:

    def __init__(self, name, parent=None):
        self._type = 'namespace'
        self._name = name
        self._initlist = ''
        self._opener = '{'
        self._access_specifier = '' #'public:'
        self._closure = '}'
        self._parent_entry = parent
        self._child_entries = list() # of Header_entry(s)
        self._value = None

        if parent:
            self._lineage = parent._lineage + [name]
            self.parent.add_child_entry(self)
        else:
            self._lineage = [name]

    def __lt__(self, other):
        '''Rich-comparison method to allow sorting.

           A Header_entry must be "less than" any another Header_entry that references it, i.e.
           you must define a value before you reference it.
        '''
        return self._less_than(other)

    def _less_than(self, other):
        lt = False
        t = f'{other._type} {other._name}'
        # \b is a "boundary" character, or specifier for a whole word
        if re.search(r'\b' + self._name + r'\b', t):
            return True
        for c in other.child_entries:
            t = f'{c._type} {c._name}'
            if re.search(r'\b' + self._name + r'\b', t):
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
        entry = self.level*'\t' + self._type + ' ' + self._name + ' ' + self._initlist + ' ' + self._opener + '\n'
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
class Typedef(Header_entry):

    def __init__(self, name, parent, typedef):
        super().__init__(name, parent)
        self._type = 'typedef'
        self._access_specifier = ''
        self._typedef = typedef

    @property
    def value(self):
        return self.level*'\t' + self._type + ' ' + self._typedef + ' ' + self._name + ';'


# -------------------------------------------------------------------------------------------------
class Enumeration(Header_entry):

    def __init__(self, name, parent, item_dict):
        super().__init__(name, parent)
        self._type = 'enum class'
        self._access_specifier = ''
        self._closure = '};'
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
        entry += ((self.level + 1)*'\t' + 'UNKNOWN\n')
        entry += (self.level*'\t' + self._closure)
        return entry


# -------------------------------------------------------------------------------------------------
class Enum_serialization(Header_entry):

    def __init__(self, name, parent, item_dict):
        super().__init__(name, parent)
        self._type = "NLOHMANN_JSON_SERIALIZE_ENUM"
        self._opener = '(' + name + ', {'
        self._closure = '})'
        self._enumerants = ['UNKNOWN'] + (list(item_dict.keys()))

    @property
    def value(self):
        entry = self.level*'\t' + self._type + ' ' + self._opener + '\n'
        for e in self._enumerants:
            entry += (self.level + 1)*'\t'
            mapping = '{' + self._name + '::' + e + ', "' + e + '"}'
            entry += (mapping + ',\n')
        entry += (self.level*'\t' + self._closure)
        return entry


# -------------------------------------------------------------------------------------------------
class Struct(Header_entry):

    def __init__(self, name, parent, superclass=''):
        super().__init__(name, parent)
        self._type = 'class'
        self._access_specifier = 'public:'
        self._closure = '};'
        if superclass:
            self._initlist = f' : public {superclass}'


# -------------------------------------------------------------------------------------------------
class Union(Header_entry):

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
class Data_element(Header_entry):

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
                    self._type = f'std::shared_ptr<{self._name}_base>'
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
                simple_type = internal_type
                # if key == self.rootname:
                #     simple_type = internal_type
                # else:
                #     simple_type = internal_type #key + '::' + internal_type
                if nested_type:
                    # 'ASHRAE205' from the composite 'ASHRAE205(RS_ID=RSXXXX)'
                    simple_type = f'std::shared_ptr<{internal_type}>'
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
        if self._is_base_class:
            s += self._namespace.value
        else:
            s += self._top_namespace.value
        s += '\n'
        for e in self._epilogue:
            s += e
        return s

    @staticmethod
    def modified_insertion_sort(obj_list):
        '''From https://stackabuse.com/sorting-algorithms-in-python/#insertionsort'''
        swapped = False
        # Start on the second element as we assume the first element is sorted
        for i in range(1, len(obj_list)):
            item_to_insert = obj_list[i]
            # And keep a reference of the index of the previous element
            j = i - 1
            # Move all items of the sorted segment forward if they are larger than the item to insert
            while j >= 0 and any(obj > item_to_insert for obj in obj_list[0:j+1]):
                obj_list[j + 1] = obj_list[j]
                swapped = True
                j -= 1
            # Insert the item
            obj_list[j + 1] = item_to_insert
        return swapped

    def translate(self, input_file_path, base_class_name):
        '''X'''
        self._source_dir = os.path.dirname(os.path.abspath(input_file_path))
        self._schema_name = os.path.splitext(os.path.splitext(os.path.basename(input_file_path))[0])[0]
        self._references.clear()
        self._fundamental_data_types.clear()
        self._preamble.clear()
        self._epilogue.clear()

        self._contents = load(input_file_path)
        enum_count = 0
        # If base_class_name is empty, I must be the base. Alternately, if base_class_name is my name
        self._is_base_class = not base_class_name or (base_class_name == self._schema_name)#('Root Data Group' in self._contents['Schema'])
        # Load meta info first (assuming that base level tag == Schema means object type == Meta)
        self._load_meta_info(self._contents['Schema'])
        self._add_include_guard(self._schema_name)
        self._add_included_headers(self._contents['Schema'].get('References'))
        if self._is_base_class:
            self._namespace = Header_entry(f'{self._schema_name}_NS')
        else:
            self._top_namespace = Header_entry(f'{base_class_name}_NS')
            self._namespace = Header_entry(f'{self._schema_name}_NS', parent=self._top_namespace)
        # First, assemble typedefs
        for base_level_tag in [tag for tag in self._contents if self._contents[tag]['Object Type'] == 'String Type']:
            Typedef(base_level_tag, self._namespace, 'std::string')
        # Second, enumerations
        for base_level_tag in [tag for tag in self._contents if self._contents[tag]['Object Type'] == 'Enumeration']:
            Enumeration(base_level_tag, self._namespace, self._contents[base_level_tag]['Enumerators'])
            Enum_serialization(base_level_tag, self._namespace, self._contents[base_level_tag]['Enumerators'])
            enum_count += 1
        # Iterate through the dictionary, looking for known types
        for base_level_tag in self._contents:
            #if 'Object Type' in self._contents[base_level_tag]:
            obj_type = self._contents[base_level_tag].get('Object Type')
            if obj_type in ['Data Group',
                            'Performance Map',
                            'Grid Variables',
                            'Lookup Variables',
                            'Rating Data Group']:
                if base_level_tag == self._schema_name and not self._is_base_class:
                    #subclass = base_level_tag + ' : public Some_base_class'
                    s = Struct(base_level_tag, self._namespace, superclass='Some_base_class')
                elif obj_type == 'Performance Map':
                    #subclass = base_level_tag + ' : public performance_map_base'
                    s = Struct(base_level_tag, self._namespace, superclass='performance_map_base')
                    self._add_member_headers(s)
                else:
                    s = Struct(base_level_tag, self._namespace)
                for data_element in self._contents[base_level_tag]['Data Elements']:
                    d = Data_element(data_element, 
                                     s, 
                                     self._contents[base_level_tag]['Data Elements'][data_element],
                                     self._fundamental_data_types,
                                     self._references
                                     )
                    self._add_member_headers(d)
        unordered = H_translator.modified_insertion_sort(self._namespace.child_entries[enum_count:])

    def _add_include_guard(self, header_name):
        s1 = f'#ifndef {header_name.upper()}_H_'
        s2 = f'#define {header_name.upper()}_H_'
        s3 = f'#endif'
        self._preamble.append(s1 + '\n' + s2 + '\n')
        self._epilogue.append(s3 + '\n')

    def _add_included_headers(self, ref_list):
        if ref_list and not self._is_base_class:
            includes = ''
            for r in ref_list:
                includes += f'#include "{r}.h"'
                includes += '\n'
            self._preamble.append(includes)
        self._preamble.append('#include <string>\n#include <vector>\n')

    def _add_member_headers(self, data_element):
        if 'shared_ptr' in data_element._type:
            m = re.search(r'\<(.*)\>', data_element._type)
            if m:
                include = f'#include "{m.group(1)}.h"\n'
                if include not in self._preamble:
                    self._preamble.append(f'#include "{m.group(1)}.h"\n')
        if data_element._initlist:
            l = data_element._initlist.split()
            if l:
                include = f'#include "{l[-1]}.h"\n'
                if include not in self._preamble:
                    self._preamble.append(f'#include "{l[-1]}.h"\n')

    def _load_meta_info(self, schema_section):
        '''Store the global/common types and the types defined by any named references.'''
        refs = list()
        if 'References' in schema_section:
            refs = schema_section['References'].copy()
        refs.append(self._schema_name)
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