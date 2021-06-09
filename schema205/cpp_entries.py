from schema205.header_entries import (Header_entry, 
                                      Struct, 
                                      Data_element, 
                                      Member_function_override, 
                                      Initialize_function, 
                                      Object_serialization)
from collections import defaultdict

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
        self._child_entries = list() # of Implementation_entry(s)
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
class Free_function_definition(Implementation_entry):

    def __init__(self, header_entry, parent=None):
        super().__init__(None, parent)
        self._func = f'void {header_entry._fname}{header_entry._args}'

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._func + ' ' + self._opener + '\n'
        for c in self._child_entries:
            entry += (c.value )
        entry += (self.level*'\t' + self._closure)
        return entry
                  
# -------------------------------------------------------------------------------------------------
class Member_function_definition(Implementation_entry):

    def __init__(self, header_entry, parent=None):
        super().__init__(None, parent)
        self._func = f'{header_entry._ret_type} {header_entry.parent._name}::{header_entry._fname}{header_entry._args}'

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

    def __init__(self, name, type, parent, is_required):
        super().__init__(name, parent)
        # self._func = [
        #     f'try {{ j.at("{name}").get_to({name}); }}',
        #     'catch (nlohmann::json::out_of_range & ex) { A205_json_catch(ex); }']
        self._func = [f'A205_json_get<{type}>(j, "{name}", {name}, {"true" if is_required else "false"});']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f + '\n'
        return entry

# -------------------------------------------------------------------------------------------------
class Owned_element_serialization(Element_serialization):

    def __init__(self, name, type, parent, is_required=False):
        super().__init__(name, type, parent, is_required)
        #self._func[0] = f'try {{ j.at("{name}").get_to(x.{name}); }}'
        self._func = [f'A205_json_get<{type}>(j, "{name}", x.{name}, {"true" if is_required else "false"});']

# -------------------------------------------------------------------------------------------------
class Owned_element_creation(Element_serialization):

    def __init__(self, name, parent, selector_dict):
        super().__init__(name, None, parent, False)
        self._func = []
        type_sel = list(selector_dict.keys())[0]
        for enum in selector_dict[type_sel]:
            self._func += [f'if (x.{type_sel} == {enum}) {{',
                           f'\tx.{name} = std::make_unique<{selector_dict[type_sel][enum]}>();',
                           f'\tif (x.{name}) {{',
                           f'\t\tx.{name}->Initialize(j.at("{name}"));',
                           '\t}',
                           '}']

# -------------------------------------------------------------------------------------------------
class Class_factory_creation(Element_serialization):

    def __init__(self, name, parent, selector_dict):
        super().__init__(name, None, parent, False)
        self._func = []
        type_sel = list(selector_dict.keys())[0]
        for enum in selector_dict[type_sel]:
            self._func += [f'if ({type_sel} == {enum}) {{',
                           f'\t{name} = {name}_factory::Create("{selector_dict[type_sel][enum]}");',
                           f'\tif ({name}) {{',
                           f'\t\t{name}->Initialize(j.at("{name}"));',
                           '\t}',
                           '}']

# -------------------------------------------------------------------------------------------------
class Serialize_from_init_func(Element_serialization):

    def __init__(self, name, parent):
        super().__init__(name, None, parent, False)
        self._func = 'x.Initialize(j);\n'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self._func

# -------------------------------------------------------------------------------------------------
class Performance_map_impl(Element_serialization):

    def __init__(self, name, parent, populates_self=False):
        super().__init__(name, None, parent, False)
        if populates_self:
            self._func = f'{name}.Populate_performance_map(this);\n'
        else:
            self._func = f'x.{name}.Populate_performance_map(&x);\n'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self._func

# -------------------------------------------------------------------------------------------------
class Grid_axis_impl(Implementation_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._func = [
            f'Add_grid_axis(performance_map, {name});\n']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f
        return entry


# -------------------------------------------------------------------------------------------------
class Grid_axis_finalize(Implementation_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._func = [
            f'performance_map->Finalize_grid();\n']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f
        return entry


# -------------------------------------------------------------------------------------------------
class Data_table_impl(Implementation_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._func = [
            f'Add_data_table(performance_map, {name});\n']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f
        return entry


# -------------------------------------------------------------------------------------------------
class Simple_return_property(Implementation_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._func = f'return "{name}";'

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._func + '\n'
        return entry


# -------------------------------------------------------------------------------------------------
class CPP_translator:

    def __init__(self):
        self._preamble = list()
        # defaultdict takes care of the factory base class
        self._implementations = defaultdict(lambda: Element_serialization)
        self._implementations['grid_variables_base'] = Grid_axis_impl
        self._implementations['lookup_variables_base'] = Data_table_impl
        self._implementations['performance_map_base'] = Element_serialization

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
            # Shortcut to avoid creating "from_json" entries for the main class, but create them
            # for all other classes. The main class relies on an "Initialize" function instead,
            # dealt-with in the next block with function overrides.
            if isinstance(entry, Struct) and entry._name not in self._namespace._name:
                # Create the "from_json" function definition (header)
                s = Struct_serialization(entry._name, self._namespace)
                for e in [c for c in entry.child_entries if isinstance(c, Data_element)]:
                    # In function body, create each "get_to" for individual data elements
                    if 'unique_ptr' in e._type:
                        Owned_element_creation(e._name, s, e._selector)
                    else:
                        Owned_element_serialization(e._name, e._type, s, e._is_required)
                    # In the special case of a performance_map subclass, add calls to its 
                    # members' Populate_performance_map functions
                    if entry._superclass == 'performance_map_base':
                        Performance_map_impl(e._name, s)
            # Initialize and Populate overrides
            if isinstance(entry, Member_function_override) or isinstance(entry, Initialize_function):
                # Create the override function definition (header) using the declaration's signature
                m = Member_function_definition(entry, self._namespace)
                # Dirty hack workaround for Name() function
                if 'Name' in entry._fname:
                    Simple_return_property(entry.parent._name, m)
                else:
                    # In function body, choose element-wise ops based on the superclass
                    for e in [c for c in entry.parent.child_entries if isinstance(c, Data_element)]:
                        if 'unique_ptr' in e._type:
                            Class_factory_creation(e._name, m, e._selector)
                            self._preamble.append(f'#include <{e._name}_factory.h>\n')
                        else:
                            if entry.parent._superclass == 'grid_variables_base':
                                Grid_axis_impl(e._name, m)
                            elif entry.parent._superclass == 'lookup_variables_base':
                                Data_table_impl(e._name, m)
                            elif entry.parent._superclass == 'performance_map_base':
                                Element_serialization(e._name, e._type, m, e._is_required)
                            else:
                                Element_serialization(e._name, e._type, m, e._is_required)
                            if entry.parent._superclass == 'performance_map_base':
                                Performance_map_impl(e._name, m, populates_self=True)
                  # Special case of grid_axis_base needs a finalize function after all grid axes 
                  # are added
                if entry.parent._superclass == 'grid_variables_base':
                    Grid_axis_finalize('', m)
            # Lastly, handle the special case of objects that need both serialization 
            # and initialization (currently a bit of a hack specific to this project)
            if isinstance(entry, Object_serialization) and entry._name in self._namespace._name:
                s = Free_function_definition(entry, self._namespace)
                Serialize_from_init_func('', s)
            else:
                self._get_items_to_serialize(entry)

    # .............................................................................................
    def _add_included_headers(self, main_header):
        self._preamble.clear()
        self._preamble.append(f'#include <{main_header}.h>\n')
