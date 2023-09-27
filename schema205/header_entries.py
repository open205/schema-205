import os
import re
from pathlib import Path
from schema205.file_io import load
from schema205.util import snake_style

def remove_prefix(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text
        
# -------------------------------------------------------------------------------------------------
class Header_entry:

    def __init__(self, name, parent=None):
        self.type = 'namespace'
        self.name = name
        self._initlist = ''
        self._opener = '{'
        self._access_specifier = ''
        self._closure = '}'
        self._parent_entry = parent
        self._child_entries = list() # of Header_entry(s)
        self.superclass = None

        if parent:
            self._parent_entry._add_child_entry(self)

    # .............................................................................................
    def __lt__(self, other):
        '''Rich-comparison method to allow sorting.

           A Header_entry must be "less than" any another Header_entry that references it, i.e.
           you must define a value before you reference it.
        '''
        return self._less_than(other)

    # .............................................................................................
    def _less_than(self, other):
        ''' '''
        lt = False
        t = f'{other.type} {other.name}'
        # \b is a "boundary" character, or specifier for a whole word
        if re.search(r'\b' + self.name + r'\b', t):
            return True
        for c in other.child_entries:
            t = f'{c.type} {c.name}'
            if re.search(r'\b' + self.name + r'\b', t):
                # Shortcut around checking siblings; if one child matches, then self < other
                return True
            else:
                # Check grandchildren
                lt = self._less_than(c)
        return lt

    # .............................................................................................
    def __gt__(self, other):
        return (other < self)

    # .............................................................................................
    def _add_child_entry(self, child):
        self._child_entries.append(child)

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self.type + ' ' + self.name + ' ' + self._initlist + ' ' + self._opener + '\n'
        entry += (self.level)*'\t' + self._access_specifier + '\n'
        for c in self._child_entries:
            entry += (c.value + '\n')
        entry += (self.level*'\t' + self._closure)
        return entry

    # .............................................................................................
    @property
    def parent(self):
        return self._parent_entry

    # .............................................................................................
    @property
    def child_entries(self):
        return self._child_entries

    # .............................................................................................
    def _get_level(self, level=0):
        if self._parent_entry:
            return self._parent_entry._get_level(level+1)
        else:
            return level

    # .............................................................................................
    @property
    def level(self):
        return self._get_level()

# -------------------------------------------------------------------------------------------------
class Typedef(Header_entry):

    def __init__(self, name, parent, typedef):
        super().__init__(name, parent)
        self.type = 'typedef'
        self._access_specifier = ''
        self._typedef = typedef

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self.type + ' ' + self._typedef + ' ' + self.name + ';'

# -------------------------------------------------------------------------------------------------
class Enumeration(Header_entry):

    def __init__(self, name, parent, item_dict):
        super().__init__(name, parent)
        self.type = 'enum class'
        self._access_specifier = ''
        self._closure = '};'
        self._enumerants = list() # list of tuple:[value, description, display_text, notes]

        enums = item_dict
        for key in enums:
            descr = enums[key].get('Description')
            displ = enums[key].get('Display Text', key)
            notes = enums[key].get('Notes')
            # Currently, CPP only cares about the key (enum name)
            self._enumerants.append((key, descr, displ, notes))

    # .............................................................................................
    @property
    def value(self):
        z = list(zip(*self._enumerants))
        enums = z[0]
        entry = self.level*'\t' + self.type + ' ' + self.name + ' ' + self._opener + '\n'
        for e in enums:
            entry += (self.level + 1)*'\t'
            entry += (e + ',\n')
        entry += ((self.level + 1)*'\t' + 'UNKNOWN\n')
        entry += (self.level*'\t' + self._closure)

        # Incorporate an enum_info map into this object
        map_type = f'const static std::unordered_map<{self.name}, enum_info>'
        entry += '\n'
        entry += self.level*'\t' + map_type + ' ' + self.name + '_info ' + self._opener + '\n'
        for e in self._enumerants:
            entry += (self.level+1)*'\t' + f'{{{self.name}::{e[0]}, {{"{e[0]}", "{e[2]}", "{e[1]}"}}}},\n'
        entry += ((self.level + 1)*'\t' + f'{{{self.name}::UNKNOWN, {{"UNKNOWN", "None","None"}}}}\n')
        entry += (self.level*'\t' + self._closure)

        return entry

# -------------------------------------------------------------------------------------------------
class Enum_serialization(Header_entry):

    def __init__(self, name, parent, item_dict):
        super().__init__(name, parent)
        self.type = "NLOHMANN_JSON_SERIALIZE_ENUM"
        self._opener = '(' + name + ', {'
        self._closure = '})'
        self._enumerants = ['UNKNOWN'] + (list(item_dict.keys()))

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self.type + ' ' + self._opener + '\n'
        for e in self._enumerants:
            entry += (self.level + 1)*'\t'
            mapping = '{' + self.name + '::' + e + ', "' + e + '"}'
            entry += (mapping + ',\n')
        entry += (self.level*'\t' + self._closure)
        return entry

# -------------------------------------------------------------------------------------------------
class Struct(Header_entry):

    def __init__(self, name, parent, superclass=''):
        super().__init__(name, parent)
        self.type = 'class'
        self._access_specifier = 'public:'
        self._closure = '};'
        if superclass:
            self.superclass = superclass
            self._initlist = f' : public {superclass}'

# -------------------------------------------------------------------------------------------------
class Data_element(Header_entry):

    def __init__(self, name, parent, element, data_types, references, find_func=None):
        super().__init__(name, parent)
        self._access_specifier = ''
        self._closure = ';'
        self._datatypes = data_types
        self._refs = references
        self._selector = dict()
        self._is_required = element.get('Required', False)

        self._create_type_entry(element, find_func)

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self.type + ' ' + self.name + self._closure

    # .............................................................................................
    def _create_type_entry(self, parent_dict, type_finder=None):
        '''Create type node.'''
        try:
            # If the type is an array, extract the surrounding [] first (using non-greedy qualifier "?")
            m = re.findall(r'\[(.*?)\]', parent_dict['Data Type'])
            if m:
                self.type = 'std::vector<' + self._get_simple_type(m[0]) + '>'
            else:
                # If the type is oneOf a set
                m = re.match(r'\((.*)\)', parent_dict['Data Type'])
                if m:
                    # Choices can only be mapped to enums, so store the mapping for future use
                    # Constraints (of selection type) are of the form 
                    # selection_key(ENUM_VAL_1, ENUM_VAL_2, ENUM_VAL_3)
                    # They connect pairwise with Data Type of the form ({Type_1}, {Type_2}, {Type_3})
                    oneof_selection_key = parent_dict['Constraints'].split('(')[0]
                    if type_finder:
                        selection_key_type = self._get_simple_type(''.join(ch for ch in type_finder(oneof_selection_key) if ch.isalnum())) + '::'
                    else:
                        selection_key_type = ''
                    types = [self._get_simple_type(t.strip()) for t in m.group(1).split(',')]
                    m_opt = re.match(r'.*\((.*)\)', parent_dict['Constraints'])
                    if not m_opt:
                        raise TypeError
                    selectors = [(selection_key_type + s.strip()) for s in m_opt.group(1).split(',')]

                    self._selector[oneof_selection_key] = dict(zip(selectors, types))
                    classname_from_name = ''.join(word.title() for word in self.name.split('_')) # CamelCase it
                    self.type = f'std::unique_ptr<{classname_from_name}Base>'
                else:
                    # 1. 'type' entry
                    self.type = self._get_simple_type(parent_dict['Data Type'])
        except KeyError as ke:
            pass

    # .............................................................................................
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
        # Look through the references to assign a source to the type. 'key' is generally a
        # schema name; its value will be a list of matchable data object names
        for key in self._refs:
            if internal_type in self._refs[key]:
                simple_type = f'{snake_style(key)}_ns::{internal_type}'
                # simple_type = internal_type
                # #
                # if key == internal_type:
                #     simple_type = f'{key}_ns::{internal_type}'
                if nested_type:
                    # e.g. 'ASHRAE205' from the composite 'ASHRAE205(RS_ID=RSXXXX)'
                    #simple_type = f'std::shared_ptr<{internal_type}>'
                    simple_type = f'{internal_type}'
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

    # .............................................................................................
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
class Lookup_struct(Header_entry):
    '''
    Special case struct for Lookup Variables. Its value property adds a LookupStruct declaration.

    This class could initialize correctly by simply deriving from Struct; however, the rich-
    comparison between Header_entry(s) only works when items being compared are not a subclass and 
    sub-subclass.
    '''

    def __init__(self, name, parent, superclass=''):
        super().__init__(name, parent)
        self.type = 'struct'
        self._closure = '};'
        if superclass:
            self.superclass = superclass
            self._initlist = f' : public {superclass}'

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self.type + ' ' + self.name + ' ' + self._initlist + ' ' + self._opener + '\n'
        entry += (self.level)*'\t' + self._access_specifier + '\n'
        for c in self._child_entries:
            entry += (c.value + '\n')
        entry += (self.level*'\t' + self._closure)

        # Add a LookupStruct that offers a SOA access rather than AOS
        entry += '\n'
        entry += self.level*'\t' + self.type + ' ' + f'{self.name}Struct' + ' ' + self._opener + '\n'
        for c in [ch for ch in self._child_entries if isinstance(ch, Data_element)]:
            m = re.match(r'std::vector\<(.*)\>', c.type)
            entry += (self.level+1)*'\t' + m.group(1) + ' ' + c.name + ';\n'
        entry += (self.level*'\t' + self._closure)
        return entry

# -------------------------------------------------------------------------------------------------
class Data_isset_element(Header_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + 'bool ' + self.name + '_is_set;'


# -------------------------------------------------------------------------------------------------
class Data_element_static_metainfo(Header_entry):

    def __init__(self, name, parent, element, meta_key):
        super().__init__(name, parent)
        self._type_specifier = 'const static'
        self.type = 'std::string_view'
        self.init_val = element.get(meta_key, '') if meta_key != 'Name' else name
        self.name = self.name + '_' + meta_key.lower()
        self._closure = ';'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self._type_specifier + ' ' + self.type + ' ' + self.name + self._closure


# -------------------------------------------------------------------------------------------------
class Data_stored_dependency(Header_entry):

    def __init__(self, name, parent, dependency_type):
        super().__init__(name, parent)
        self._type_specifier = 'static'
        self.type = dependency_type
        self._closure = ';'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self._type_specifier + ' ' + self.type + ' ' + self.name + self._closure


# -------------------------------------------------------------------------------------------------
class Functional_header_entry(Header_entry):

    def __init__(self, f_ret, f_name, f_args, name, parent):
        super().__init__(name, parent)
        self.fname = f_name
        self.ret_type = f_ret
        self.args = f_args
        self._closure = ';'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + ' '.join([self.ret_type, self.fname, self.args]) + self._closure

# -------------------------------------------------------------------------------------------------
class Member_function_override(Functional_header_entry):

    def __init__(self, f_ret, f_name, f_args, name, parent):
        super().__init__(f_ret, f_name, f_args, name, parent)
        self._closure = ' override;'

# -------------------------------------------------------------------------------------------------
class Object_serialization(Functional_header_entry):

    def __init__(self, name, parent):
        super().__init__('void', 
                         'from_json', 
                         f'(const nlohmann::json& j, {name}& x)', 
                         name, 
                         parent)

# -------------------------------------------------------------------------------------------------
class Initialize_function(Functional_header_entry):
    ''' Deprecated '''

    def __init__(self, name, parent):
        super().__init__('void', 'initialize', '(const nlohmann::json& j)', name, parent)

# -------------------------------------------------------------------------------------------------
class Grid_var_counter_enum(Header_entry):

    def __init__(self, name, parent, item_dict):
        super().__init__(name, parent)
        self.type = 'enum'
        self._access_specifier = ''
        self._closure = '};'
        self._enumerants = list()

        for key in item_dict:
            self._enumerants.append(f'{key}_index')

    # .............................................................................................
    @property
    def value(self):
        enums = self._enumerants
        entry = self.level*'\t' + self.type + ' ' + self.name + ' ' + self._opener + '\n'
        for e in enums:
            entry += (self.level + 1)*'\t'
            entry += (e + ',\n')
        entry += ((self.level + 1)*'\t' + 'index_count\n')
        entry += (self.level*'\t' + self._closure)
        return entry

# -------------------------------------------------------------------------------------------------
class Calculate_performance_overload(Functional_header_entry):

    def __init__(self, f_ret, f_args, name, parent, n_return_values):
        super().__init__(f_ret, 'calculate_performance', '(' + ', '.join(f_args) + ')', name, parent)
        self.args_as_list = f_args
        self.n_return_values = n_return_values

    # .............................................................................................
    @property
    def value(self):
        complete_decl = self.level*'\t' + 'using PerformanceMapBase::calculate_performance;\n'
        complete_decl += self.level*'\t' + ' '.join([self.ret_type, self.fname, self.args]) + self._closure
        return complete_decl


# -------------------------------------------------------------------------------------------------
class H_translator:

    def __init__(self):
        self._references = dict()
        self._fundamental_data_types = dict()
        self._preamble = list()
        self._doxynotes = '/// @note  This class has been auto-generated. Local changes will not be saved!\n'
        self._epilogue = list()
        self._data_group_types = ['Data Group',
                                  'Performance Map',
                                  'Grid Variables',
                                  'Lookup Variables',
                                  'Rating Data Group']


    # .............................................................................................
    def __str__(self):
        s = ''
        for p in self._preamble:
            s += p
        s += '\n'
        s += self._doxynotes
        s += '\n'
        s += self.root.value
        s += '\n'
        for e in self._epilogue:
            s += e
        return s

    @property
    def root(self):
        return self._top_namespace

    # .............................................................................................
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

    # .............................................................................................
    def _list_objects_of_type(self, object_type_or_list):
        if isinstance(object_type_or_list, str):
            return [tag for tag in self._contents if self._contents[tag]['Object Type'] == object_type_or_list]
        elif isinstance(object_type_or_list, list):
            return [tag for tag in self._contents if self._contents[tag]['Object Type'] in object_type_or_list]

    # .............................................................................................
    def translate(self, input_file_path, container_class_name, schema_base_class_name=None):
        '''X'''
        abs_input_file_path = Path(input_file_path).resolve()
        self._source_dir = abs_input_file_path.parent #os.path.dirname(os.path.abspath(input_file_path))
        self._schema_name = Path(abs_input_file_path.stem).stem #os.path.splitext(os.path.splitext(os.path.basename(input_file_path))[0])[0]
        self._references.clear()
        self._fundamental_data_types.clear()
        self._preamble.clear()
        self._epilogue.clear()

        self._contents = load(input_file_path)

        self._fundamental_base_class = schema_base_class_name if schema_base_class_name else 'RSInstanceBase'

        # Load meta info first (assuming that base level tag == Schema means object type == Meta)
        self._load_meta_info(self._contents['Schema'])
        self._add_include_guard(snake_style(self._schema_name))
        self._add_included_headers(self._contents['Schema'].get('References'))

        # Create "root" node(s)
        self._top_namespace = Header_entry(f'{container_class_name}')
        self._namespace = Header_entry(f'{snake_style(self._schema_name)}_ns', parent=self._top_namespace)

        # First, assemble typedefs
        for base_level_tag in self._list_objects_of_type('String Type'):
            Typedef(base_level_tag, self._namespace, 'std::string')
        # Second, enumerations
        for base_level_tag in self._list_objects_of_type('Enumeration'):
            Enumeration(base_level_tag, self._namespace, self._contents[base_level_tag]['Enumerators'])
        # Collect member objects and their children
        for base_level_tag in self._list_objects_of_type('Meta'):
            s = Struct(base_level_tag, self._namespace)
            d = Data_element_static_metainfo(base_level_tag.lower(),
                                             s,
                                             self._contents[base_level_tag],
                                             'Title')
            d = Data_element_static_metainfo(base_level_tag.lower(),
                                             s,
                                             self._contents[base_level_tag],
                                             'Version')
            d = Data_element_static_metainfo(base_level_tag.lower(),
                                             s,
                                             self._contents[base_level_tag],
                                             'Description')
        # If there's no root data group, create a class to hold the shared_ptr so it can be initialized later
        if self._root_data_group not in self._list_objects_of_type(self._data_group_types):
            self._root_data_group = self._schema_name # assuming schema file name is CamelCase
            s = Struct(self._root_data_group, self._namespace)
            d = Data_stored_dependency('logger', s, 'std::shared_ptr<Courierr::Courierr>')
        # 205-specific classes
        for base_level_tag in self._list_objects_of_type(self._data_group_types):
            if base_level_tag == self._root_data_group:
                s = Struct(base_level_tag, self._namespace, superclass=self._fundamental_base_class)
                self._add_member_headers(s)
                self._add_function_overrides(s, self._fundamental_base_class)
                d = Data_stored_dependency('logger', s, 'std::shared_ptr<Courierr::Courierr>')
            elif self._contents[base_level_tag].get('Object Type') == 'Grid Variables':
                s = Struct(base_level_tag, self._namespace, superclass='GridVariablesBase')
                self._add_member_headers(s)
                self._add_function_overrides(s, 'GridVariablesBase')
                e = Grid_var_counter_enum('', s, self._contents[base_level_tag]['Data Elements'])
            elif self._contents[base_level_tag].get('Object Type') == 'Lookup Variables':
                s = Lookup_struct(base_level_tag, self._namespace, superclass='LookupVariablesBase')
                self._add_member_headers(s)
                self._add_function_overrides(s, 'LookupVariablesBase')
                e = Grid_var_counter_enum('', s, self._contents[base_level_tag]['Data Elements'])
            elif self._contents[base_level_tag].get('Object Type') == 'Performance Map':
                s = Struct(base_level_tag, self._namespace, superclass='PerformanceMapBase')
                self._add_member_headers(s)
                self._add_function_overrides(s, 'PerformanceMapBase')
            else:
                # Catch-all for when a class of name _schema_name isn't present in the schema
                s = Struct(base_level_tag, self._namespace)
            
            for data_element in self._contents[base_level_tag]['Data Elements']:
                d = Data_element(data_element, 
                                    s, 
                                    self._contents[base_level_tag]['Data Elements'][data_element],
                                    self._fundamental_data_types,
                                    self._references,
                                    self._search_nodes_for_datatype
                                    )
                self._add_member_headers(d)
            for data_element in self._contents[base_level_tag]['Data Elements']:
                d = Data_isset_element(data_element, s)
            for data_element in self._contents[base_level_tag]['Data Elements']:
                d = Data_element_static_metainfo(data_element, 
                                                 s, 
                                                 self._contents[base_level_tag]['Data Elements'][data_element],
                                                 'Units')
            for data_element in self._contents[base_level_tag]['Data Elements']:
                d = Data_element_static_metainfo(data_element, 
                                                 s, 
                                                 self._contents[base_level_tag]['Data Elements'][data_element],
                                                 'Description')
            for data_element in self._contents[base_level_tag]['Data Elements']:
                d = Data_element_static_metainfo(data_element, 
                                                 s, 
                                                 self._contents[base_level_tag]['Data Elements'][data_element],
                                                 'Name')
        H_translator.modified_insertion_sort(self._namespace.child_entries)
        # PerformanceMapBase object needs sibling grid/lookup vars to be created, so parse last
        self._add_performance_overloads()

        # Final passes through dictionary in order to add elements related to serialization
        for base_level_tag in self._list_objects_of_type('Enumeration'):
            Enum_serialization(base_level_tag, 
                               self._namespace, 
                               self._contents[base_level_tag]['Enumerators'])
        for base_level_tag in ([tag for tag in self._contents 
            if self._contents[tag].get('Object Type') in self._data_group_types]):
                # from_json declarations are necessary in top container, as the header-declared
                # objects might be included and used from elsewhere.
                Object_serialization(base_level_tag, self._namespace)

        return self._fundamental_base_class

    # .............................................................................................
    def _add_include_guard(self, header_name):
        s1 = f'#ifndef {header_name.upper()}_H_'
        s2 = f'#define {header_name.upper()}_H_'
        s3 = f'#endif'
        self._preamble.append(s1 + '\n' + s2 + '\n')
        self._epilogue.append(s3 + '\n')

    # .............................................................................................
    def _add_included_headers(self, ref_list):
        if ref_list:
            includes = ''
            for r in ref_list:
                includes += f'#include <{snake_style(r)}.h>'
                includes += '\n'
            self._preamble.append(includes)
        self._preamble.append('#include <string>\n#include <vector>\n#include <nlohmann/json.hpp>\n#include <typeinfo_205.h>\n#include <courierr/courierr.h>\n')

    # .............................................................................................
    def _add_member_headers(self, data_element):
        if 'unique_ptr' in data_element.type:
            m = re.search(r'\<(.*)\>', data_element.type)
            if m:
                include = f'#include <{snake_style(m.group(1))}.h>\n'
                if include not in self._preamble:
                    self._preamble.append(include)
                # This is a perfect opportunity to cache the fundamental base class owned by the
                # top-level container
                self._fundamental_base_class = m.group(1)
        if data_element._initlist:
            l = data_element._initlist.split()
            if l:
                include = f'#include <{snake_style(l[-1])}.h>\n'
                if include not in self._preamble:
                    self._preamble.append(include)

    # .............................................................................................
    def _load_meta_info(self, schema_section):
        '''Store the global/common types and the types defined by any named references.'''
        refs = list()
        self._root_data_group = schema_section.get('Root Data Group')
        if 'References' in schema_section:
            refs = schema_section['References'].copy()
        refs.insert(0,self._schema_name) # prepend the current file to references list so that 
                                         # objects are found locally first
        for ref_file in refs:
            ext_dict = load(self._source_dir.joinpath(ref_file).with_suffix('.schema.yaml')) #load(os.path.join(self._source_dir, ref_file + '.schema.yaml'))
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

    # .............................................................................................
    def _add_function_overrides(self, parent_node, base_class_name):
        '''Get base class virtual functions to be overridden.'''
        base_class = Path(__file__).parent.joinpath( 
                                  'libtk205_fixed_src',
                                  'include', 
                                  f'{snake_style(base_class_name)}.h')
        try:
            with open(base_class) as b:
                for line in b:
                    if base_class_name not in line:
                        m = re.match(r'\s*virtual\s(.*)\s(.*)\((.*)\)', line)
                        if m:
                            f_ret_type = m.group(1)
                            f_name = m.group(2)
                            f_args = f'({m.group(3)})'
                            Member_function_override(f_ret_type, f_name, f_args, '', parent_node)
        except:
            pass
        
    # .............................................................................................
    def _add_performance_overloads(self, parent_node=None):
        ''' '''
        if not parent_node:
            parent_node = self.root
        for entry in parent_node.child_entries:
            if entry.parent and entry.superclass == 'PerformanceMapBase':
                for lvstruct in [lv for lv in entry.parent.child_entries 
                                   if lv.superclass == 'LookupVariablesBase'
                                   and remove_prefix(lv.name, 'LookupVariables') == remove_prefix(entry.name, 'PerformanceMap')]:
                    f_ret = f'{lvstruct.name}Struct'
                    n_ret = len([c for c in lvstruct.child_entries if isinstance(c, Data_element)])
                    # for each performance map, find GridVariables sibling of PerformanceMap, that has a matching name
                    for gridstruct in [gridv for gridv in entry.parent.child_entries 
                                    if gridv.superclass == 'GridVariablesBase'
                                    and remove_prefix(gridv.name, 'GridVariables') == remove_prefix(entry.name, 'PerformanceMap')]:
                        f_args = list()
                        for ce in [c for c in gridstruct.child_entries if isinstance(c, Data_element)]:
                            f_args.append(' '.join(['double', ce.name]))
                        f_args.append('Btwxt::InterpolationMethod performance_interpolation_method = Btwxt::InterpolationMethod::linear')
                        Calculate_performance_overload(f_ret, f_args, '', entry, n_ret)
            else:
                self._add_performance_overloads(entry)

    # .............................................................................................
    def _search_nodes_for_datatype(self, data_element):
        for listing in self._contents:
            if 'Data Elements' in self._contents[listing]:
                for element in self._contents[listing]['Data Elements']:
                    if (element == data_element 
                        and 'Data Type' in self._contents[listing]['Data Elements'][element]):
                        return self._contents[listing]['Data Elements'][element]['Data Type']

