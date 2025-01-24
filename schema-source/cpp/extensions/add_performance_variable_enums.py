from dataclasses import dataclass
from lattice.cpp.header_entries import HeaderEntry, Struct, DataElement
from lattice.cpp.header_translator import PluginInterface

@dataclass
class CounterEnum(HeaderEntry):
    elements: list

    def __post_init__(self):
        super().__post_init__()
        self.type = "enum"
        self._closure = "};"
        self._enumerants = list()

        for element in self.elements:
            self._enumerants.append(f"{element}_index")
        self._enumerants.append("index_count");

        self.trace()

    def __str__(self):
        enums = self._enumerants
        entry = f"{self._indent}{self.type} {self._opener}\n"
        entry += ",\n".join([f"{self._indent}\t{e}" for e in enums])
        entry += f"\n{self._indent}{self._closure}"
        return entry


class GridVarCounterEnumPlugin(PluginInterface, base_class="GridVariablesTemplate"):
    """"""
    def process_data_group(self, parent_node: HeaderEntry):
        for entry in parent_node.child_entries:
            if isinstance(entry, Struct) and entry.superclass == "ashrae205::GridVariablesTemplate":
                data_elements = [child.name for child in entry.child_entries if isinstance(child, DataElement)]
                e = CounterEnum(entry.name, entry, data_elements)
            else:
                self.process_data_group(entry)


class LookupVarCounterEnumPlugin(PluginInterface, base_class="LookupVariablesTemplate"):
    """"""
    def process_data_group(self, parent_node: HeaderEntry):
        for entry in parent_node.child_entries:
            if isinstance(entry, Struct) and entry.superclass == "ashrae205::LookupVariablesTemplate":
                data_elements = [child.name for child in entry.child_entries if isinstance(child, DataElement)]
                e = CounterEnum(entry.name, entry, data_elements)
            else:
                self.process_data_group(entry)
