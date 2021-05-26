import itertools

def get_representation_node(representation, lineage):
    node = representation
    for name in lineage:
        node = node[name]
    return node

def create_grid_set(grid_variables, order):
    lists = []
    if len(grid_variables) != len(order):
        raise Exception(f"order: {order} must contain the keys of 'grid_variables': {grid_variables}")

    for var in order:
        if var not in grid_variables:
            raise Exception(f"{var} not found in {order}")

        if len(grid_variables[var]) == 0:
            #TODO: Probably should be an exception
            return None
        lists.append(grid_variables[var])

    grid = list(zip(*itertools.product(*lists)))
    grid_set = {}
    for i, var in enumerate(order):
        grid_set[var] = grid[i]

    return grid_set

def process_grid_set(grid_set):
    grid_vars = {}
    for var in grid_set:
        grid_vars[var] = list(set(grid_set[var]))
        grid_vars[var].sort()
    return grid_vars

def unique_name_with_index(name, list_of_names, max_chars=31):
    # 31 characters is max length for XLSX spreadsheet name
    modified_name = name[:max_chars]
    if modified_name not in list_of_names:
        return modified_name
    else:
        i = 0
        searching = True
        while searching:
            modified_name = modified_name[:max_chars - len(f"{i}")]
            if f"{modified_name}{i}" in list_of_names:
                i += 1
            else:
                searching = False
                return f"{modified_name}{i}"