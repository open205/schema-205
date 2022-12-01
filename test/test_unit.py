import schema205
import os

'''
Unit tests
'''

def test_resolve_ref():
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","ASHRAE205.schema.json"))

    node = schema.resolve_ref("ASHRAE205.schema.json#/definitions/Metadata")
    assert('title' not in node)

def test_get_schema_node():

    # Node in external reference
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0001.schema.json"))
    node = schema.get_schema_node(['description', 'product_information', 'compressor_type'])
    assert('enum' in node)

    # Node in internal reference
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0003.schema.json"))
    node = schema.get_schema_node(['description', 'product_information', 'impeller_type'])
    assert('enum' in node)

    # Node in nested RS
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0002.schema.json"))
    node = schema.get_schema_node(['performance', 'indoor_fan_representation', 'description', 'product_information', 'impeller_type'])
    assert('enum' in node)

    # Array node
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0001.schema.json"))
    node = schema.get_schema_node(['performance','evaporator_liquid_type','liquid_components'])
    assert('items' in node)

    # Node in array
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0001.schema.json"))
    node = schema.get_schema_node(['performance','evaporator_liquid_type','liquid_components','liquid_constituent'])
    assert('enum' in node)

    # Ambiguous node (without defined options, get_schema_node will return the first match it finds)
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0003.schema.json"))
    node = schema.get_schema_node(['performance','performance_map','grid_variables'],[None, 0, None])
    node2 = schema.get_schema_node(['performance','performance_map','grid_variables'],[None, 1, None])
    assert(node != node2)

    # Root node
    node = schema.get_schema_node([])
    assert('required' in node)

    # Root node of nested RS
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0002.schema.json"))
    node = schema.get_schema_node(['performance','indoor_fan_representation'])
    assert('ASHRAE 205' not in node['description'])

def test_create_grid_set():
    rep = schema205.load_json('examples/RS0004/DX-Constant-Efficiency.RS0004.a205.json')
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0004.schema.json"))
    grid_set = schema.create_grid_set(rep, ['performance','performance_map_cooling','grid_variables'])
    table_length = 1
    grid_vars = rep['performance']['performance_map_cooling']['grid_variables']
    for var in grid_vars:
        table_length *= len(grid_vars[var])

    for var in grid_vars:
        assert(table_length == len(grid_set[var]))

def test_get_grid_variable_order():

    # Typical case
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0004.schema.json"))
    grid_vars_names = ['outdoor_coil_entering_dry_bulb_temperature','indoor_coil_entering_relative_humidity', 'indoor_coil_entering_dry_bulb_temperature', 'indoor_coil_air_mass_flow_rate', 'compressor_sequence_number', 'ambient_absolute_air_pressure']
    lineage = ['performance','performance_map_cooling','grid_variables']
    order = schema.get_grid_variable_order(lineage,grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 1
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0003.schema.json"))
    grid_vars_names = ['standard_air_volumetric_flow_rate','static_pressure_difference']
    lineage = ['performance','performance_map','grid_variables']
    order = schema.get_grid_variable_order(lineage,grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 2
    grid_vars_names = ['speed_number','static_pressure_difference']
    lineage = ['performance','performance_map','grid_variables']
    order = schema.get_grid_variable_order(lineage,grid_vars_names)
    assert(order == grid_vars_names)

def test_process_grid_set():
    rep = schema205.load_json('examples/RS0004/DX-Constant-Efficiency.RS0004.a205.json')
    grid_vars = rep['performance']['performance_map_cooling']['grid_variables']
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","RS0004.schema.json"))
    grid_set = schema.create_grid_set(rep, ['performance','performance_map_cooling','grid_variables'])
    grid_vars2 = schema205.util.process_grid_set(grid_set)
    assert(grid_vars == grid_vars2)

def test_get_schema_rs_title():
    schema = schema205.A205Schema(os.path.join(os.path.dirname(__file__),'..','build',"schema","ASHRAE205.schema.json"))

    title = schema.get_rs_title('RS0001')
    assert(title == "Liquid-Cooled Chiller")