def print_regex(regex_str, title=None):
  print(f"{title}:\n")
  print(regex_str)
  print("\n\n")
  print(regex_str.replace('\\','\\\\').replace("\"","\\\""))
  print("\n\n")

# Data types

base_types = "(Numeric|String|Integer|Boolean|Null)"
string_types = "(UUID|Date|Timestamp|Version|Pattern)"
type_names = "[A-Z]([A-Z]|[a-z]|[0-9])*"
element_names = "([a-z]+)(_([a-z]|[0-9])+)*"
data_groups = f"\\{{{type_names}\\}}"
enumerations = f"<{type_names}>"
optional_base_types = f"{base_types}{{1}}(\\/{base_types})*"
single_type = f"({optional_base_types}|{string_types}|{data_groups}|{enumerations})"
alternatives = f"\\({single_type}(,\\s*{single_type})+\\)"
arrays = f"\\[{single_type}\\]"
data_types = f"{single_type}|{alternatives}|{arrays}"

# TODO add tests?
'''
Number

Numeric

String

number

Boolean

Integer

Null

UUID

Numeric/Null/String


Numeric/Null/<String>

Numeric/Null

[Numeric]

{Something}

<CompressorType>

[Numeric/Null/String]

({Something}, {SomethingElse},Numeric,<EnumType>)
'''

print_regex(data_types,"Data Types")

# Values
number = "([-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?)"
string = "\".*\""
enumerator = "([A-Z]([A-Z]|[0-9])*)(_([A-Z]|[0-9])+)*"
boolean = "True|False"
values = f"({number})|({string})|({enumerator})|({boolean})"
enum_list = f"\(({enumerator})(, *({enumerator}))*\)"

print_regex(values,"Values")

# Constraints
ranges = f"(>|>=|<=|<){number}"
multiples = f"%{number}"
data_element_value = f"({element_names})=({values})"
sets = f"\\[{number}(, {number})*\\]"
selectors = f"({element_names})({enum_list})"
string_pattern = f"({string})"
constraints = f"({ranges})|({multiples})|({sets})|({data_element_value})|({selectors})|({string_pattern})"

'''
>=0
>-0
<1.0
<=1.0e5
rs_id=RS0001
%2.5
[2008, 2009, 2010]
'''

print_regex(constraints,"Constraints")

# Conditional Requirements
conditional_requirements = f"if ({element_names})(!?=({values}))?"

'''
if rs_id=RS0001
if a
if x_dd_dd!=True
'''

print_regex(conditional_requirements,"Conditional Requirements")
