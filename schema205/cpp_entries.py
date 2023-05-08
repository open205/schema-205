from schema205.header_entries import (Header_entry, 
                                      Struct, 
                                      Lookup_struct,
                                      Data_element, 
                                      Data_isset_element,
                                      Data_element_static_metainfo,
                                      Data_stored_dependency,
                                      Member_function_override, 
                                      Object_serialization,
                                      Calculate_performance_overload)
from schema205.util import snake_style
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
class Data_element_static_initialization(Implementation_entry):

    def __init__(self, header_entry, parent=None):
        super().__init__(None, parent)
        type_spec = header_entry._type_specifier.replace('static', '').strip(' ')
        self._func = ' '.join([type_spec, header_entry.type, f'{header_entry.parent.name}::{header_entry.name}', '=', f'"{header_entry.init_val}";'])

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._func + '\n'
        return entry
                  
# -------------------------------------------------------------------------------------------------
class Static_dependency_initialization(Implementation_entry):

    def __init__(self, header_entry, parent=None):
        super().__init__(None, parent)
        type_spec = header_entry._type_specifier.replace('static', '').strip(' ')
        self._func = ' '.join([type_spec, header_entry.type, f'{header_entry.parent.name}::{header_entry.name}', '{};'])

    # .............................................................................................
    @property
    def value(self):
        entry = self.level*'\t' + self._func + '\n'
        return entry
                  
# -------------------------------------------------------------------------------------------------
class Free_function_definition(Implementation_entry):

    def __init__(self, header_entry, parent=None):
        super().__init__(None, parent)
        self._func = f'void {header_entry.fname}{header_entry.args}'

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
        args = header_entry.args
        if hasattr(header_entry, 'args_as_list'):
            args = '(' + ', '.join([a.split('=')[0] for a in header_entry.args_as_list]) + ')'
        self._func = f'{header_entry.ret_type} {header_entry.parent.name}::{header_entry.fname}{args}'

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

    def __init__(self, name, type, parent, is_required, root_data_group=None):
        super().__init__(name, parent)
        self._func = [f'a205_json_get<{type}>(j, *{root_data_group}::logger, "{name}", {name}, {name}_is_set, {"true" if is_required else "false"});']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f + '\n'
        return entry

# -------------------------------------------------------------------------------------------------
class Owned_element_serialization(Element_serialization):

    def __init__(self, name, type, parent, is_required, root_data_group):
        super().__init__(name, type, parent, is_required, root_data_group)
        if root_data_group:
            self._func = [f'a205_json_get<{type}>(j, *{root_data_group}::logger, "{name}", x.{name}, x.{name}_is_set, {"true" if is_required else "false"});']
        else:
            self._func = [f'a205_json_get<{type}>(j, *logger, "{name}", x.{name}, x.{name}_is_set, {"true" if is_required else "false"});']

# -------------------------------------------------------------------------------------------------
class Owned_element_creation(Element_serialization):

    def __init__(self, name, parent, selector_dict, root_data_group):
        super().__init__(name, None, parent, False, root_data_group)
        self._func = []
        type_sel = list(selector_dict.keys())[0]
        for enum in selector_dict[type_sel]:
            self._func += [f'if (x.{type_sel} == {enum}) {{',
                           f'\tx.{name} = std::make_unique<{selector_dict[type_sel][enum]}>();',
                           f'\tif (x.{name}) {{',
                           f'\t\tx.{name}->initialize(j.at("{name}"));',
                           '\t}',
                           '}']

# -------------------------------------------------------------------------------------------------
class Class_factory_creation(Element_serialization):

    def __init__(self, name, parent, selector_dict, root_data_group):
        super().__init__(name, None, parent, False, root_data_group)
        self._func = []
        type_sel = list(selector_dict.keys())[0]
        for enum in selector_dict[type_sel]:
            self._func += [f'if ({type_sel} == {enum}) {{',
                           f'\t{name} = {name}Factory::create("{selector_dict[type_sel][enum]}");',
                           f'\tif ({name}) {{',
                           f'\t\t{name}->initialize(j.at("{name}"), {root_data_group}::logger);',
                           '\t}',
                           '}']

# -------------------------------------------------------------------------------------------------
class Serialize_from_init_func(Element_serialization):

    def __init__(self, name, parent):
        super().__init__(name, None, parent, False)
        self._func = 'x.initialize(j);\n'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self._func

# -------------------------------------------------------------------------------------------------
class Performance_map_impl(Element_serialization):

    def __init__(self, name, parent, root_data_group, populates_self=False):
        super().__init__(name, None, parent, False)
        if populates_self:
            self._func = f'{name}.populate_performance_map(this);\n'
        else:
            self._func = f'x.{name}.populate_performance_map(&x);\n'

    # .............................................................................................
    @property
    def value(self):
        return self.level*'\t' + self._func

# -------------------------------------------------------------------------------------------------
class Grid_axis_impl(Implementation_entry):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._func = [
            f'add_grid_axis(performance_map, {name});\n']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f
        return entry


# -------------------------------------------------------------------------------------------------
class Grid_axis_finalize(Implementation_entry):

    def __init__(self, name, parent, root_data_group):
        super().__init__(name, parent)
        self._func = [
            f'performance_map->finalize_grid({root_data_group}::logger);\n']

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
            f'add_data_table(performance_map, {name});\n']

    # .............................................................................................
    @property
    def value(self):
        entry = ''
        for f in self._func:
            entry += self.level*'\t' + f
        return entry


# -------------------------------------------------------------------------------------------------
class Performance_overload_impl(Element_serialization):
    def __init__(self, header_entry, parent):
        super().__init__(None, None, parent, None)
        self._func = []
        args = ', '.join([f'{a[1]}' for a in [arg.split(' ') for arg in header_entry.args_as_list[:-1]]])
        self._func.append(f'std::vector<double> target {{{args}}};')
        self._func.append('auto v = PerformanceMapBase::calculate_performance(target, performance_interpolation_method);')
        init_str = f'{header_entry.ret_type} s {{'
        for i in range(header_entry.n_return_values):
            init_str += f'v[{i}], '
        init_str += '};'
        self._func.append(init_str)
        self._func.append('return s;')


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
        s += self._top_namespace.value
        s += '\n'
        return s

    # .............................................................................................
    def translate(self, container_class_name, header_translator):
        '''X'''
        self._add_included_headers(header_translator._schema_name)

        # Create "root" node(s)
        self._top_namespace = Implementation_entry(f'{container_class_name}')
        self._namespace = (
            Implementation_entry(f'{snake_style(header_translator._schema_name)}_ns', parent=self._top_namespace))

        self._get_items_to_serialize(header_translator.root, header_translator._root_data_group)

    # .............................................................................................
    def _get_items_to_serialize(self, header_tree: Header_entry, root_data_group: str):
        for entry in header_tree.child_entries:
            # Shortcut to avoid creating "from_json" entries for the main class, but create them
            # for all other classes. The main class relies on an "Initialize" function instead,
            # dealt-with in the next block with function overrides.
            if ((isinstance(entry, Struct) or isinstance(entry, Lookup_struct))
               and entry.name not in self._namespace._name):
                if any([isinstance(c, Data_element) for c in entry.child_entries]):
                    # Create the "from_json" function definition (header)
                    s = Struct_serialization(entry.name, self._namespace)
                    for e in [c for c in entry.child_entries if isinstance(c, Data_element)]:
                        # In function body, create each "get_to" for individual data elements
                        if 'unique_ptr' in e.type:
                            Owned_element_creation(e.name, s, e._selector, root_data_group)
                        else:
                            Owned_element_serialization(e.name, e.type, s, e._is_required, root_data_group)
                        # In the special case of a performance_map subclass, add calls to its 
                        # members' Populate_performance_map functions
                        if entry.superclass == 'PerformanceMapBase':
                            Performance_map_impl(e.name, s, root_data_group)
            # Initialize static members
            if (isinstance(entry, Data_element_static_metainfo)):
                Data_element_static_initialization(entry, self._namespace)
            if isinstance(entry, Data_stored_dependency) and '{}' not in entry.name:
                Static_dependency_initialization(entry, self._namespace)
            # Initialize and Populate overrides (Currently the only Member_function_override is the Initialize override)
            if isinstance(entry, Member_function_override):
                # Create the override function definition (header) using the declaration's signature
                m = Member_function_definition(entry, self._namespace)
                # Dirty hack workaround for Name() function
                if 'Name' in entry.fname:
                    Simple_return_property(entry.parent.name, m)
                else:
                    # In function body, choose element-wise ops based on the superclass
                    for e in [c for c in entry.parent.child_entries if isinstance(c, Data_element)]:
                        if 'unique_ptr' in e.type:
                            Class_factory_creation(e.name, m, e._selector, root_data_group)
                            self._preamble.append(f'#include <{e.name}_factory.h>\n')
                        else:
                            if entry.parent.superclass == 'GridVariablesBase':
                                Grid_axis_impl(e.name, m)
                            elif entry.parent.superclass == 'LookupVariablesBase':
                                Data_table_impl(e.name, m)
                            elif entry.parent.superclass == 'PerformanceMapBase':
                                Element_serialization(e.name, e.type, m, e._is_required, root_data_group)
                            else:
                                Element_serialization(e.name, e.type, m, e._is_required, root_data_group)
                            if entry.parent.superclass == 'PerformanceMapBase':
                                Performance_map_impl(e.name, m, root_data_group, populates_self=True)
                  # Special case of grid_axis_base needs a finalize function after all grid axes 
                  # are added
                if entry.parent.superclass == 'GridVariablesBase':
                    Grid_axis_finalize('', m, root_data_group)
            if isinstance(entry, Calculate_performance_overload):
                m = Member_function_definition(entry, self._namespace)
                for e in [c for c in entry.parent.child_entries if isinstance(c, Data_element)]:
                    # Build internals of Calculate_performance function
                    if e.name == 'grid_variables':
                        Performance_overload_impl(entry, m)
            # Lastly, handle the special case of objects that need both serialization 
            # and initialization (currently a bit of a hack specific to this project)
            if isinstance(entry, Object_serialization) and entry.name in self._namespace._name:
                s = Free_function_definition(entry, self._namespace)
                Serialize_from_init_func('', s)
            else:
                self._get_items_to_serialize(entry, root_data_group)

    # .............................................................................................
    def _add_included_headers(self, main_header):
        self._preamble.clear()
        self._preamble.append(f'#include <{snake_style(main_header)}.h>\n#include <loadobject_205.h>\n')
