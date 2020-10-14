from schema205.header_entries import Header_entry
from schema205.header_entries import Data_element
from schema205.header_entries import Struct
from schema205.header_entries import Member_function_override

# -------------------------------------------------------------------------------------------------
class Implementation_entry:

    def __init__(self, name, parent=None):
        self._type = 'namespace'
        self._scope = ''
        self._name = name
        self._opener = '{'
        self._access_specifier = ''
        self._closure = '}'
        self._parent_entry = parent
        self._child_entries = list() # of Header_entry(s)
        self._value = None

        if parent:
            self._lineage = parent._lineage + [name]
            self._parent_entry._add_child_entry(self)
        else:
            self._lineage = [name]

    # .............................................................................................
    def _add_child_entry(self, child):
        self._child_entries.append(child)

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

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._type + ' ' + self._name + ' ' + ' ' + self._opener + '\n'
        entry += (self.level)*'\t' + self._access_specifier + '\n'
        for c in self._child_entries:
            entry += (c.value + '\n')
        entry += (self.level*'\t' + self._closure)
        return entry

# -------------------------------------------------------------------------------------------------
class Member_function_serialization(Implementation_entry):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._func = f'void {name}::Initialize(const nlohmann::json& j)'

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._func + ' ' + self._opener + '\n'
        for c in self._child_entries:
            entry += (c.value )
        entry += (self.level*'\t' + self._closure)
        return entry
                  
# -------------------------------------------------------------------------------------------------
class Struct_serialization(Implementation_entry):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._func = f'void from_json(const nlohmann::json& j, {name}& x)'

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._func + ' ' + self._opener + '\n'
        for c in self._child_entries:
            entry += (c.value )
        entry += (self.level*'\t' + self._closure)
        return entry
                  
# -------------------------------------------------------------------------------------------------
class Element_serialization(Implementation_entry):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._func = [
            f'try {{ j.at("{name}").get_to(x.{name}); }}'+'\n',
            'catch (nlohmann::json::out_of_range & ex) { A205_json_catch(ex); }\n']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f
        return entry


# -------------------------------------------------------------------------------------------------
class CPP_translator:

    def __init__(self):
        self._preamble = list()

    # .............................................................................................
    def __str__(self):
        s = ''
        for p in self._preamble:
            s += p
        s += '\n'
        if self._is_top_container:
            s += self._namespace.value
        else:
            s += self._top_namespace.value
        s += '\n'
        return s

    # .............................................................................................
    def translate(self, container_class_name, header_tree):
        '''X'''
        self._add_included_headers(header_tree._schema_name)

        # If container_class_name is empty, I must be the top container. 
        # Also true if container_class_name is my name.
        self._is_top_container = ( 
            not container_class_name or (container_class_name == header_tree._schema_name))

        # Create "root" node(s)
        if self._is_top_container:
            self._namespace = Implementation_entry(f'{header_tree._schema_name}_NS')
        else:
            self._top_namespace = Implementation_entry(f'{container_class_name}_NS')
            self._namespace = (
                Implementation_entry(f'{header_tree._schema_name}_NS', parent=self._top_namespace))

        self._get_items_to_serialize(header_tree.root)

    # .............................................................................................
    def _get_items_to_serialize(self, header_tree):
        for entry in header_tree.child_entries:
            if isinstance(entry, Struct) and not any(isinstance(obj, Member_function_override) for obj in entry.child_entries):
                s = Struct_serialization(entry._name, self._namespace)
                for e in [c for c in entry.child_entries if isinstance(c, Data_element)]:
                    Element_serialization(e._name, s)
            elif isinstance(entry, Member_function_override):
                m = Member_function_serialization(entry.parent._name, self._namespace)
                for e in [c for c in entry.parent.child_entries if isinstance(c, Data_element)]:
                    Element_serialization(e._name, m)
            else:
                self._get_items_to_serialize(entry)

    # .............................................................................................
    def _add_included_headers(self, main_header):
        self._preamble.clear()
        self._preamble.append(f'#include "{main_header}.h"\n')
        #self._preamble.append('#include <string>\n#include <vector>\n')
