import os
import json
import posixpath
import jsonschema
from .util import create_grid_set
from .util import get_representation_node_and_rs_selections
from .util import get_rs_index
from .file_io import load_json

def iterdict(d, dict_as_list, level=0):
    for key in d:
        preamble = 'Level ' + str(level) + ' ' + '  '*level + ' ' + key
        if isinstance(d[key], dict):
            dict_as_list.append(preamble + ': [dict]')
            iterdict(d[key], dict_as_list, level+1)
        else:
            dict_as_list.append(preamble + ': ' + str(d[key]))


class A205Schema:
    def __init__(self, schema_path):
        with open(schema_path, "r") as schema_file:
            uri_path = os.path.abspath(os.path.dirname(schema_path))
            if os.sep != posixpath.sep:
                uri_path = posixpath.sep + uri_path

            resolver = jsonschema.RefResolver(f'file://{uri_path}/', schema_path)

            self.validator = jsonschema.Draft7Validator(json.load(schema_file), resolver=resolver)

    def process_errors(self, errors, rs_index, parent_level = 0):
        '''
        This method collects relevant error messages using recursion for 'oneOf' or 'anyOf' validations
        '''
        messages = []
        for error in errors:
            if error.validator in ['oneOf','anyOf','allOf']:
                schema_node = self.get_schema_node(list(error.absolute_path))
                if 'RS' in schema_node:
                    rs_index = get_rs_index(schema_node['RS'])
                if rs_index is not None:
                    rs_errors = []
                    for rs_error in error.context:
                        if rs_error.relative_schema_path[0] == rs_index:
                            rs_errors.append(rs_error)
                else:
                    rs_errors = error.context
                messages += self.process_errors(rs_errors, rs_index, len(error.path))
            else:
                if len(error.path) >= parent_level:
                    messages.append(f"{error.message} ({'.'.join([str(x) for x in error.path])})")
        if len(messages) == 0 and parent_level == 0:
            for error in errors:
                messages.append(f"{error.message} ({'.'.join([str(x) for x in error.path])})")
        return messages

    def validate(self, instance):
        errors = sorted(self.validator.iter_errors(instance), key=lambda e: e.path)
        if len(errors) == 0:
            print(f"Validation successful for {instance['description']}")
        else:
            if 'rs_id' in instance:
                rs_id = instance['rs_id']
                rs_index = get_rs_index(rs_id)
            else:
                rs_id = "RS????"
                rs_index = None
            messages = self.process_errors(errors, rs_index)
            messages = [f"{i}. {message}" for i, message in enumerate(messages, start=1)]
            message_str = '\n  '.join(messages)
            raise Exception(f"Validation failed for \"{instance['description']}\" ({rs_id}) with {len(messages)} errors:\n  {message_str}")

    def resolve(self, node, step_in=True, parent_node=None):
        '''
        Return this node with any references replaced by entire referenced object.
        If step_in is True, return the node's properties instead.
        '''
        if isinstance(node, dict) and 'if' in node:
            node = node['then']
            resolution = node

        if '$ref' in node:
            resolution = self.resolve_ref(node['$ref'])
            # Carry other contents from location of reference
            for item in node:
                if item != '$ref':
                    resolution[item] = node[item]
        else:
            resolution = node

        if step_in and 'properties' in resolution:
            return resolution['properties']
        else:
            return resolution

    def resolve_ref(self, ref):
        scope, resolution = self.validator.resolver.resolve(ref)
        self.validator.resolver.push_scope(scope)
        return resolution

    def get_schema(self):
        return self.validator.schema

    def trace_lineage(self, node, lineage, options, parent_node=None):
        '''
        Search through lineage for the schema node one generation at a time.

        node: node to trace into
        lineage: remaining lineage to trace
        options: indices for any oneOf nodes
        parent_node: aux node to check for additional property information
        '''
        for item in node:
            # Case where the node passed in contains additional properties fleshed out in allOf 
            if item == 'allOf':
                if options[0] is not None:
                    resolution = self.resolve(node['allOf'][options[0]])
                    if lineage[0] in resolution:
                        #return self.resolve(resolution[lineage[0]])
                        return self.trace_lineage(self.resolve(resolution[lineage[0]]),lineage[1:],options[1:],self.resolve(resolution[lineage[0]], False))
                for option in node['allOf']:
                    resolution = self.resolve(option) # each #ref will be evaluated separately
                    if lineage[0] in resolution:
                        if len(lineage) == 1:
                            return self.resolve(resolution, False)
                        else:
                            next_node = self.resolve(resolution[lineage[0]], True)
                            if lineage[1] in next_node:
                                try:
                                    return self.trace_lineage(next_node,lineage[1:],options[1:],self.resolve(resolution[lineage[0]], False))
                                except KeyError:
                                    pass
            if item == lineage[0]:
                if len(lineage) == 1:
                    # This is the last node
                    return self.resolve(node[item],False)
                else:
                    if '$ref' in node[item] or 'type' in node[item]:
                        # node is not a "placeholder"; has contained information
                        next_node = self.resolve(node[item])
                        if 'items' in next_node:
                            next_node = self.resolve(next_node['items'])
                        return self.trace_lineage(next_node, lineage[1:],options[1:], self.resolve(node[item],False))
                    else:
                        # node is a placeholder; find its info in parent
                        return self.trace_lineage(parent_node,lineage,options)

        raise KeyError(f"'{lineage[0]}' not found in schema.")

    def get_schema_node(self, lineage, options=None):
        if len(lineage) == 0:
            return self.resolve(self.validator.schema, step_in=False)
        if options is None:
            options = [None]*len(lineage)
        schema = self.resolve(self.validator.schema)
        try:
            return self.trace_lineage(schema, lineage, options, self.resolve(self.validator.schema, False))
        except KeyError as ke:
            return None

    def get_schema_version(self):
        return self.validator.schema["version"]

    def get_rs_title(self, rs):
        return self.resolve_ref(f'{rs}.schema.json#/title')

    def get_grid_variable_order(self, rs_selections, lineage, grid_vars):
        '''
        Get the order of grid variables.

        TODO: Don't know if we can always rely on jsonschema always preserving order
        '''
        if lineage[-1] != 'grid_variables':
            raise Exception(f"{lineage[-1]} is not a 'grid_variables' data group.")
        parent_schema_node = self.get_schema_node(lineage[:-2], rs_selections[:-2])
        if 'allOf' in parent_schema_node:
            # Alternate performance maps allowed. Make sure we get the right one
            for option in parent_schema_node['allOf']:
                # allOf resolutions are 2-deep dictionaries; resolve twice
                option = self.resolve(self.resolve(option)[lineage[-2]])
                for var in grid_vars:
                    option_grid_vars = self.resolve(option['grid_variables'])
                    if var not in option_grid_vars:
                        schema_node = None
                        break
                    else:
                        schema_node = option_grid_vars
                if schema_node:
                    break
        else:
            schema_node = self.get_schema_node(lineage, rs_selections)['properties']
        order = []

        if not schema_node:
            raise Exception(f"Unable to find schema for grid variables: {grid_vars}")

        for item in schema_node:
            order.append(item)
        return order

    def create_grid_set(self, representation, lineage):
        grid_var_content, rs_selections = get_representation_node_and_rs_selections(representation, lineage)
        order = self.get_grid_variable_order(rs_selections, lineage,[x for x in grid_var_content])
        return create_grid_set(grid_var_content, order)

def validate(file_path):
    a205schema = A205Schema(os.path.join(os.path.dirname(__file__),'..','build','schema',"ASHRAE205.schema.json"))
    a205schema.validate(load_json(file_path))

def validate_directory(example_dir):
    errors = []
    for example in os.listdir(example_dir):
        example_path = os.path.join(example_dir,example)
        if os.path.isdir(example_path):
            errors += validate_directory(example_path)
        else:
            if '~$' not in example:  # Ignore temporary Excel files
                try:
                    validate(os.path.join(example_dir,example))
                except Exception as e: # Change to tk205 Exception
                    errors.append(e)
    if len(errors) > 0:
        error_str = '\n\n'.join([f"{e}" for e in errors])
        raise Exception(f"{error_str}")
    return errors
