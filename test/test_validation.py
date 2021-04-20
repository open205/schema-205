import schema205
import os
import pytest

EXAMPLES_DIR = 'examples'
SCHEMA_DIR = os.path.join('build','schema')

def collect_examples(example_dir):
    paths = []
    names = []

    for example in sorted(os.listdir(example_dir)):
        example_path = os.path.join(example_dir,example)
        if os.path.isdir(example_path):
            paths += collect_examples(example_path)[0]
            names += collect_examples(example_path)[1]
        else:
            if ".a205.json" in example:
                paths.append(os.path.join(example_dir,example))
                names.append(example)
    return paths, names

paths, names = collect_examples(EXAMPLES_DIR)

@pytest.mark.parametrize("example",paths, ids=names)
def test_validate(example):
    schema_name = schema205.load_json(example)["metadata"]["schema"]
    schema_path = os.path.join(SCHEMA_DIR,f"{schema_name}.schema.json")
    schema205.schema.validate(example, schema_path)

BAD_EXAMPLE_DIR = 'test/bad-examples'
bad_examples = sorted(os.listdir(BAD_EXAMPLE_DIR))
@pytest.mark.parametrize("example",bad_examples, ids=bad_examples)
def test_invalidate(example):
    with pytest.raises(Exception):
        schema_path = os.path.join(SCHEMA_DIR,"RS0001.schema.json")
        schema205.schema.validate(os.path.join(BAD_EXAMPLE_DIR,example),schema_path)
