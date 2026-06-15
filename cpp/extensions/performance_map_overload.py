import re
import logging
from dataclasses import dataclass, field
from lattice.cpp.header_entries import DataElement, Struct, HeaderEntry, FunctionalHeaderEntry, MemberFunctionOverrideDeclaration
from lattice.cpp.header_translator import HeaderEntryExtensionInterface
from lattice.cpp.cpp_entries import ImplementationEntry, ElementSerialization, CPPExtensionInterface


def remove_prefix(text, prefix):
    return text[len(prefix) :] if text.startswith(prefix) else text

# Performance map implementation plugin needs to know about the class(es) used for the custom header
# entry plugin, so both are defined in this file


# HeaderEntry extension class and plugin

@dataclass
class PerformanceMapOverload(FunctionalHeaderEntry):
    """ """
    name: str = field(init=False, default="")
    _f_name: str = field(init=False)
    lookup_types: list[str]

    def __post_init__(self):
        self._f_name = "calculate_performance"
        self.args = f"({', '.join(self._f_args)})"
        super().__post_init__()

    def __str__(self):
        complete_decl = self._indent + "using ashrae205::PerformanceMapTemplate::calculate_performance;\n"
        complete_decl += self._indent + " ".join([self._f_ret, self._f_name, self.args]) + self._closure
        return complete_decl

class PerformanceOverloadPlugin(HeaderEntryExtensionInterface, base_class="PerformanceMapTemplate"):
    """"""
    def process_data_group(self, parent_node: HeaderEntry):
        for entry in parent_node.child_entries:
            if isinstance(entry, Struct) and entry.superclass == "ashrae205::PerformanceMapTemplate" and entry.parent:
                for lvstruct in [
                    lv
                    for lv in entry.parent.child_entries
                    if isinstance(lv, Struct) and lv.superclass == "ashrae205::LookupVariablesTemplate"
                    and remove_prefix(lv.name, "LookupVariables") == remove_prefix(entry.name, "PerformanceMap")
                ]:
                    f_ret = f"{lvstruct.name}Struct"
                    ret_types = ["::".join(c.scoped_innertype) if c.scoped_innertype[0] else c.scoped_innertype[1] for c in lvstruct.child_entries if isinstance(c, DataElement)]
                    # for each performance map, find GridVariables sibling of PerformanceMap, that has a matching name
                    for gridstruct in [
                        gridv
                        for gridv in entry.parent.child_entries
                        if isinstance(gridv, Struct) and gridv.superclass == "ashrae205::GridVariablesTemplate"
                        and remove_prefix(gridv.name, "GridVariables") == remove_prefix(entry.name, "PerformanceMap")
                    ]:
                        f_args = list()
                        for ce in [c for c in gridstruct.child_entries if isinstance(c, DataElement)]:
                            f_args.append(" ".join(["double", ce.name]))
                        f_args.append("Btwxt::InterpolationMethod performance_interpolation_method = Btwxt::InterpolationMethod::linear")
                        PerformanceMapOverload(entry, f_ret, f_args, ret_types)
            else:
                self.process_data_group(entry)

# ImpementationEntry extension classes and plugin

@dataclass
class DataTableImplementation(ImplementationEntry):
    def __post_init__(self):
        super().__post_init__()
        self._func = f"add_data_table(performance_map, {self._name});"

    def __str__(self):
        return self._indent + self._func + "\n"

@dataclass
class GridAxisImplementation(ImplementationEntry):
    def __post_init__(self):
        super().__post_init__()
        self._func = f"add_grid_axis(performance_map, {self._name});"

    def __str__(self):
        return self._indent + self._func + "\n"


@dataclass
class PerformanceMapImplementation(ImplementationEntry):
    _populates_self: bool

    def __post_init__(self):
        super().__post_init__()
        if self._populates_self:
            self._func = f"{self._name}.populate_performance_map(this);"
        else:
            self._func = f"x.{self._name}.populate_performance_map(&x);"

    def __str__(self):
        return self._indent + self._func + "\n"


@dataclass
class GridAxisFinalize(ImplementationEntry):
    def __post_init__(self):
        super().__post_init__()
        self._func = f"performance_map->finalize_grid(logger);"

    def __str__(self):
        return self._indent + self._func + "\n"


@dataclass
class PerformanceOverloadImplementation(ImplementationEntry):
    _header_entry: PerformanceMapOverload

    def __post_init__(self):
        super().__post_init__()
        self._funclines = []
        args = ", ".join([f"{a[1]}" for a in [arg.split(" ") for arg in self._header_entry._f_args[:-1]]])
        self._funclines.append(f"std::vector<double> target {{{args}}};")
        self._funclines.append(
            "auto v = calculate_performance(target, performance_interpolation_method);"
        )
        init_str = f"{self._header_entry._f_ret} s {{"
        struct_item_index = list(range(len(self._header_entry.lookup_types)))
        init_str += ", ".join([(f"v[{i}]" if self._header_entry.lookup_types[i] == "double" else f"static_cast<{self._header_entry.lookup_types[i]}>(v[{i}])") for i in struct_item_index])
        init_str += "};"
        self._funclines.append(init_str)
        self._funclines.append("return s;")

        self.trace()

    def __str__(self):
        return "\n".join([(self._indent + f) for f in self._funclines]) + "\n"


class PerformanceImplPlugin(CPPExtensionInterface):
    """"""
    def process_data_group(self, h_entry: HeaderEntry, parent_node: ImplementationEntry):

        if isinstance(h_entry, Struct) and len([c for c in h_entry.child_entries if isinstance(c, DataElement)]):
            for data_element_entry in [c for c in h_entry.child_entries if isinstance(c, DataElement)]:
                # In the special case of a performance_map subclass, add calls to its
                # members' Populate_performance_map functions
                if h_entry.superclass == "ashrae205::PerformanceMapTemplate":
                    PerformanceMapImplementation(data_element_entry, parent_node, False)
        if isinstance(h_entry, MemberFunctionOverrideDeclaration) and isinstance(h_entry.parent, Struct):
            # In function body, choose element-wise ops based on the superclass
            for data_element_entry in [c for c in h_entry.parent.child_entries if isinstance(c, DataElement)]:
                if h_entry.parent.superclass == "ashrae205::GridVariablesTemplate":
                    GridAxisImplementation(data_element_entry, parent_node)
                elif h_entry.parent.superclass == "ashrae205::LookupVariablesTemplate":
                    DataTableImplementation(data_element_entry, parent_node)
                elif h_entry.parent.superclass == "ashrae205::PerformanceMapTemplate":
                    ElementSerialization(data_element_entry, parent_node)
                    PerformanceMapImplementation(data_element_entry, parent_node, True)
            # Special case of grid_axis_base needs a finalize function after all grid axes
            # are added
            if h_entry.parent.superclass == "ashrae205::GridVariablesTemplate":
                GridAxisFinalize(h_entry, parent_node)

        if isinstance(h_entry, PerformanceMapOverload):
            for data_element_entry in [c for c in h_entry.parent.child_entries if isinstance(c, DataElement)]:
                # Build internals of calculate_performance function
                if data_element_entry.name == "grid_variables":
                    PerformanceOverloadImplementation(h_entry, parent_node)
