import re
import copy
from dataclasses import dataclass
from lattice.cpp.header_entries import DataElement, HeaderEntry, Struct
# from lattice.cpp.header_entries import register_data_group_operation
from lattice.cpp.header_translator import HeaderEntryExtensionInterface

@dataclass
class LookupStruct(HeaderEntry):
    """
    Special case struct for Lookup Variables. Its str overload adds a LookupStruct declaration.
    """
    def __post_init__(self):
        super().__post_init__()
        self.name = f"{self.name}Struct"
        self.type = "struct"
        self._closure = "};"

        self.trace()

    def __str__(self):
        # Add a LookupStruct that offers a SOA access rather than AOS
        struct = f"{self._indent}{self.type} {self.name} {self._opener}\n"
        for c in [ch for ch in self.child_entries if isinstance(ch, DataElement)]:
            m = re.match(r'std::vector\<(.*)\>', c.type)
            assert m is not None
            struct += f"{self._indent}\t{m.group(1)} {c.name};\n"
        struct += f"{self._indent}{self._closure}"

        return struct


class LookupStructPlugin(HeaderEntryExtensionInterface, base_class="LookupVariablesTemplate"):
    """"""
    def process_data_group(self, parent_node: HeaderEntry):
        for entry in parent_node.child_entries:
            if isinstance(entry, Struct) and entry.superclass == "ashrae205::LookupVariablesTemplate":
                ls = LookupStruct(entry.name, entry.parent)
                for child in [ch for ch in entry.child_entries if isinstance(ch, DataElement)]:
                    ls._add_child_entry(copy.copy(child))
            else:
                self.process_data_group(entry)
