import json
import yaml
import os
from collections import OrderedDict
import re

def get_extension(file):
    return os.path.splitext(file)[1]


def load(input_file_path):
    ext = get_extension(input_file_path).lower()
    if (ext == '.json'):
        with open(input_file_path, 'r') as input_file:
            return json.load(input_file)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(input_file_path, 'r') as input_file:
            return yaml.load(input_file, Loader=yaml.FullLoader)
    else:
        raise Exception(f"Unsupported input \"{ext}\".")


def dump(content, output_file_path):
    ext = get_extension(output_file_path).lower()
    if (ext == '.json'):
        with open(output_file_path,'w') as output_file:
            json.dump(content, output_file, indent=4)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(output_file_path, 'w') as out_file:
            yaml.dump(content, out_file, sort_keys=False)

    else:
        raise Exception(f"Unsupported output \"{ext}\".")


def compare_dicts(original, modified, error_list):
    o = load(original)
    m = load(modified)
    return dict_compare(o, m, error_list, level=0, lineage=None, hide_value_mismatches=False)


# https://stackoverflow.com/questions/4527942/comparing-two-dictionaries-and-checking-how-many-key-value-pairs-are-equal
def dict_compare(d1, d2, errors, level=0, lineage=None, hide_value_mismatches=False, hide_key_mismatches=False):
    if not lineage:
        lineage = list()
    if d1 == d2:
        return True
    else:
        if isinstance(d1, dict) and isinstance(d2, dict):
            d1_keys = sorted(list(d1.keys()))
            d2_keys = sorted(list(d2.keys()))
            if d1_keys != d2_keys:
                added = [k for k in d2_keys if k not in d1_keys]
                removed = [k for k in d1_keys if k not in d2_keys]
                err = ''
                if added and not hide_key_mismatches:
                    errors.append(f'Keys added to second dictionary at level {level}, lineage {lineage}: {added}')
                if removed and not hide_key_mismatches:
                    errors.append(f'Keys removed from first dictionary at level {level}, lineage {lineage}: {removed}.')
                return False
            else:
            # Enter this part of the code if both dictionaries have all keys shared at this level
                shared_keys = d1_keys
                for k in shared_keys:
                    dict_compare(d1[k], d2[k], errors, level+1, lineage+[k], hide_value_mismatches, hide_key_mismatches)
        elif d1 != d2:
            # Here, we could use the util.objects_near_equal to compare objects. Currently, d1 and
            # d2 may have any type, i.e. float 1.0 will be considered equal to int 1.
            err = f'Mismatch in values: "{d1}" vs. "{d2}" at lineage {lineage}.'
            if not hide_value_mismatches:
                errors.append(err)
            return False


# -------------------------------------------------------------------------------------------------
class DataGroup:

    def __init__(self, name, type_list, ref_list=None):
        self._name = name
        self._types = type_list
        self._refs = ref_list


    def add_data_group(self, group_name, group_subdict):
        elements = {'type': 'object',
                    'properties' : dict()}
        required = list()
        for e in group_subdict:
            element = group_subdict[e]
            if 'Description' in element:
                elements['properties'][e] = {'description' : element['Description']}
            if 'Data Type' in element:
                self._create_type_entry(group_subdict[e], elements['properties'][e])
            if 'Units' in element:
                elements['properties'][e]['units'] = element['Units']
            if 'Notes' in element:
                elements['properties'][e]['notes'] = element['Notes']
            if 'Required' in element:
                required.append(e)
        if required:
            elements['required'] = required
        elements['additionalProperties'] = False

        return {group_name : elements}


    def _create_type_entry(self, parent_dict, target_dict):
        '''Create type node and its nested nodes if necessary.'''
        try:
            # If the type is an array, extract the surrounding [] first (using non-greedy qualifier "?")
            m = re.findall(r'\[(.*?)\]', parent_dict['Data Type'])
            if m:
                # 1. 'type' entry
                target_dict['type'] = 'array'
                # 2. 'm[in/ax]Items' entry
                if len(m) > 1:
                    # Parse ellipsis range-notation e.g. '[1..]'
                    mnmx = re.match(r'([0-9]*)(\.*\.*)([0-9]*)', m[1])
                    target_dict['minItems'] = int(mnmx.group(1))
                    if (mnmx.group(2) and mnmx.group(3)):
                        target_dict['maxItems'] = int(mnmx.group(3))
                    elif not mnmx.group(2):
                        target_dict['maxItems'] = int(mnmx.group(1))
                # 3. 'items' entry
                target_dict['items'] = dict()
                self._get_simple_type(m[0], target_dict['items'])
                #target_dict['items'][k] = v
                if 'Range' in parent_dict:
                    self._get_simple_minmax(parent_dict['Range'], target_dict['items'])
            else:
                # If the type is oneOf a set
                m = re.findall(r'^\((.*)\)', parent_dict['Data Type'])
                if m:
                    target_dict['oneOf'] = list()
                    choices = m[0].split(',')
                    for c in choices:
                        c = c.strip()
                        target_dict['oneOf'].append(dict())
                        self._get_simple_type(c, target_dict['oneOf'][-1])
                else:
                    # 1. 'type' entry
                    self._get_simple_type(parent_dict['Data Type'], target_dict)
                    # 2. 'm[in/ax]imum' entry
                    self._get_simple_minmax(parent_dict['Range'], target_dict)
        except KeyError as ke:
            #print('KeyError; no key exists called', ke)
            pass


    def _get_simple_type(self, type_str, target_dict_to_append):
        ''' Return the internal type described by type_str, along with its json-appropriate key.

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
                # Rare case of a nested specification e.g. 'ASHRAE205(rs_id=RS0005)'
                internal_type = m.group(2).split('(')[0]
                nested_type = m_nested.group(1)
            else:
                internal_type = m.group(2)
        else:
            internal_type = type_str
        # Look through the references to assign a source to the type
        for key in self._refs:
            if internal_type in self._refs[key]:
                internal_type = key + '.schema.json#/definitions/' + internal_type
                target_dict_to_append['$ref'] = internal_type
                if nested_type:
                    # Always in the form 'rs_id=RSXXXX'
                    target_dict_to_append['rs_id'] = nested_type.split('=')[1]
                return

        try:
            if '/' in type_str:
                # e.g. "Numeric/Null" becomes a list of 'type's
                #return ('type', [self._types[t] for t in type_str.split('/')])
                target_dict_to_append['type'] = [self._types[t] for t in type_str.split('/')]
            else:
                target_dict_to_append['type'] = self._types[type_str]
        except KeyError:
            print('Type not processed:', type_str)
        return


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
class Enumeration:

    def __init__(self, name, description=None):
        self._name = name
        self._enumerants = list() # list of tuple:[value, description, display_text, notes]
        self.entry = dict()
        self.entry[self._name] = dict()
        if description:
            self.entry[self._name]['description'] = description

    def add_enumerator(self, value, description=None, display_text=None, notes=None):
        '''Store information grouped as a tuple per enumerant.'''
        self._enumerants.append((value, description, display_text, notes))

    def create_dictionary_entry(self):
        '''Convert information currently grouped per enumerant, into json groups for
           the whole enumeration.
        '''
        z = list(zip(*self._enumerants))
        enums = {'type': 'string',
                 'enum' : z[0]}
        if any(z[2]):
            enums['enum_text'] = z[2]
        if any(z[1]):
            enums['descriptions'] = z[1]
        if any(z[3]):
            enums['notes'] = z[3]
        self.entry[self._name] = {**self.entry[self._name], **enums}
        return self.entry


# -------------------------------------------------------------------------------------------------
class JSON_translator:
    def __init__(self):
        self._references = dict()
        self._fundamental_data_types = dict()


    def load_common_schema(self, input_file_path):
        '''Load and process a yaml schema into its json schema equivalent.'''
        self._schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                        'title': None,
                        'description': None,
                        'definitions' : dict()}
        self._references.clear()
        self._source_dir = os.path.dirname(os.path.abspath(input_file_path))
        self._schema_name = os.path.splitext(os.path.splitext(os.path.basename(input_file_path))[0])[0]
        self._fundamental_data_types.clear()
        self._contents = load(input_file_path)
        sch = dict()
        # Iterate through the dictionary, looking for known types
        for base_level_tag in self._contents:
            if 'Object Type' in self._contents[base_level_tag]:
                obj_type = self._contents[base_level_tag]['Object Type']
                if obj_type == 'Meta':
                    self._load_meta_info(self._contents[base_level_tag])
                if obj_type == 'String Type':
                    if 'Is Regex' in self._contents[base_level_tag]:
                        sch = {**sch, **({base_level_tag : {"type":"string", "regex":True}})}
                    else:
                        sch = {**sch, **({base_level_tag : {"type":"string", "pattern":self._contents[base_level_tag]['JSON Schema Pattern']}})}
                if obj_type == 'Enumeration':
                    sch = {**sch, **(self._process_enumeration(base_level_tag))}
                if obj_type in ['Data Group',
                                'Performance Map',
                                'Grid Variables',
                                'Lookup Variables',
                                'Rating Data Group']:
                    dg = DataGroup(base_level_tag, self._fundamental_data_types, self._references)
                    sch = {**sch, **(dg.add_data_group(base_level_tag,
                                     self._contents[base_level_tag]['Data Elements']))}
        self._schema['definitions'] = sch
        return self._schema


    def _load_meta_info(self, schema_section):
        '''Store the global/common types and the types defined by any named references.'''
        self._schema['title'] = schema_section['Title']
        self._schema['description'] = schema_section['Description']
        if 'Version' in schema_section:
            self._schema['version'] = schema_section['Version']
        if 'Root Data Group' in schema_section:
            self._schema['$ref'] = self._schema_name + '.schema.json#/definitions/' + schema_section['Root Data Group']
        # Create a dictionary of available external objects for reference
        refs = list()
        if 'References' in schema_section:
            refs = schema_section['References']
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
            for base_item in [name for name in ext_dict if ext_dict[name]['Object Type'] == 'Data Type']:
                self._fundamental_data_types[base_item] = ext_dict[base_item]['JSON Schema Type']


    def _process_enumeration(self, name_key):
        ''' Collect all Enumerators in an Enumeration block. '''
        enums = self._contents[name_key]['Enumerators']
        description = self._contents[name_key].get('Description')
        definition = Enumeration(name_key, description)
        for key in enums:
            try:
                descr = enums[key]['Description']  if 'Description'  in enums[key] else None
                displ = enums[key]['Display Text'] if 'Display Text' in enums[key] else None
                notes = enums[key]['Notes']        if 'Notes'        in enums[key] else None
                definition.add_enumerator(key, descr, displ, notes)
            except TypeError: # key's value is None
                definition.add_enumerator(key)
        return definition.create_dictionary_entry()


# -------------------------------------------------------------------------------------------------
def print_comparison(original_dir, generated_dir, file_name_root, err):
    '''Compare generated dictionary to original; send results to stdout.'''
    same = compare_dicts(os.path.join(original_dir, file_name_root + '.schema.json'),
                         os.path.join(generated_dir, file_name_root + '.schema.json'),
                         err)
    if not same:
        print(f'\nError(s) while matching {file_name_root}: Original(1) vs Generated(2)')
        for e in err:
            print(e)
    else:
        print(f"Translation of {file_name_root} successful.")

# -------------------------------------------------------------------------------------------------

def translate_file(input_file_path, output_file_path):
    j = JSON_translator()
    schema_instance = j.load_common_schema(input_file_path)
    dump(schema_instance, output_file_path)

def translate_dir(input_dir_path, output_dir_path):
    j = JSON_translator()
    for file_name in sorted(os.listdir(input_dir_path)):
        if '.schema.yaml' in file_name:
            file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
            schema_instance = j.load_common_schema(os.path.join(input_dir_path,file_name))
            dump(schema_instance, os.path.join(output_dir_path, file_name_root + '.schema.json'))


if __name__ == '__main__':
    import sys

    source_dir_path = os.path.join(os.path.dirname(__file__),'..','schema-source')
    build_dir_path = os.path.join(os.path.dirname(__file__),'..','build')
    if not os.path.exists(build_dir_path):
        os.mkdir(build_dir_path)
    schema_dir_path = os.path.join(build_dir_path,'schema')
    if not os.path.exists(schema_dir_path):
        os.mkdir(schema_dir_path)

    if len(sys.argv) == 2:
        file_name_root = sys.argv[1]
        translate_file(os.path.join(source_dir_path, f'{file_name_root}.schema.yaml'), os.path.join(schema_dir_path, file_name_root + '.schema.json'))
    else:
        translate_dir(source_dir_path, schema_dir_path)
