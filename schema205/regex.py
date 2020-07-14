base_types = "(Numeric|String|Integer|Boolean|Null)"
string_types = "(UUID|Date|Timestamp|Version|Pattern)"
type_names = "[A-Z]([A-Z]|[a-z]|[0-9])*"
element_names = "([A-Z]*|[a-z]*)(_([a-z]*|[0-9]*)|([A-Z]*|[0-9]*))*"
data_groups = f"\\{{{type_names}(\\({element_names}=(.*)\\))?\\}}"
enumerations = f"<{type_names}>"
optional_base_types = f"{base_types}{{1}}(\\/{base_types})*"
single_type = f"({optional_base_types}|{string_types}|{data_groups}|{enumerations})"
alternatives = f"\\({single_type}(,\\s*{single_type})+\\)"
arrays = f"\\[{single_type}\\]"
final_regex = f"{single_type}|{alternatives}|{arrays}"

# TODO add tests?

# Actual string
print(final_regex)

print("\n\n")

# With proper JSON escaping
print(final_regex.replace('\\','\\\\'))