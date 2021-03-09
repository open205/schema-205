import os
from schema205.header_entries import H_translator
from schema205.file_io import dump
from schema205.cpp_entries import CPP_translator
from schema205.generate_factory_templates import generate_factory_headers, generate_factory_source

# -------------------------------------------------------------------------------------------------
def translate_to_header(input_file_path, output_file_root, base_class='foo_base', container=''):
    h = H_translator()
    h.translate(input_file_path, container, base_class)
    dump(str(h), output_file_root + '.h')

# -------------------------------------------------------------------------------------------------
def translate_to_source(input_file_path, output_file_root, base_class='foo_base', container=''):
    h = H_translator()
    h.translate(input_file_path, container, base_class)
    c = CPP_translator()
    c.translate(container, h)
    dump(str(c), output_file_root + '.cpp')

# -------------------------------------------------------------------------------------------------
def translate_all_to_headers(input_dir_path, output_dir_path, container=''):
    '''
    '''
    h = H_translator()
    # Sort input file so the container source is first
    src_files = [src for src in sorted(os.listdir(input_dir_path),
                                       key=lambda f:int(f.startswith(container)),
                                       reverse=True) if '.schema.yaml' in src]
    # Extract base class info from "container" src file first
    file_name_root = os.path.splitext(os.path.splitext(src_files[0])[0])[0]
    base_class = h.translate(os.path.join(input_dir_path, src_files[0]), container)
    dump(str(h), os.path.join(output_dir_path, file_name_root + '.h'))
    # Process remaining src using base class assumption
    for file_name in src_files[1:]:
        file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
        h.translate(os.path.join(input_dir_path, file_name), container, base_class)
        dump(str(h), os.path.join(output_dir_path, file_name_root + '.h'))
        if file_name_root != container:
            factory_header = generate_factory_headers(file_name_root, base_class, container)
            dump(factory_header, os.path.join(output_dir_path, file_name_root + '_factory.h'))

# -------------------------------------------------------------------------------------------------
def translate_all_to_source(input_dir_path, output_dir_path, container=''):
    h = H_translator()
    # Sort input file so the container source is first
    src_files = [src for src in sorted(os.listdir(input_dir_path),
                                       key=lambda f:int(f.startswith(container)),
                                       reverse=True) if '.schema.yaml' in src]
    # Extract base class info from "container" src file first
    file_name_root = os.path.splitext(os.path.splitext(src_files[0])[0])[0]
    base_class = h.translate(os.path.join(input_dir_path, src_files[0]), container)
    c = CPP_translator()
    c.translate(container, h)
    dump(str(c), os.path.join(output_dir_path, file_name_root + '.cpp'))
    # Process remaining src using base class assumption
    for file_name in src_files[1:]:
        file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
        h.translate(os.path.join(input_dir_path, file_name), container, base_class)
        c.translate(container, h)
        dump(str(c), os.path.join(output_dir_path, file_name_root + '.cpp'))
        if file_name_root != container:
            factory_src = generate_factory_source(file_name_root, container)
            dump(factory_src, os.path.join(output_dir_path, file_name_root + '_factory.cpp'))

# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import glob

    source_dir = os.path.join(os.path.dirname(__file__),'..','schema-source')
    build_dir = os.path.join(os.path.dirname(__file__),'..','build')
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    dump_dir = os.path.join(build_dir,'cpp')
    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)

    if len(sys.argv) == 4:
        file_name_root = sys.argv[1]
        base_class = sys.argv[2]
        container = sys.argv[3]
        translate_to_header(os.path.join(source_dir, f'{file_name_root}.schema.yaml'), 
                            os.path.join(dump_dir, file_name_root),
                            base_class, 
                            container)
    elif len(sys.argv) == 3:
        base_class = sys.argv[1]
        container = sys.argv[2]
        translate_all_to_headers(source_dir, dump_dir, base_class, container)
    else:
        print('Script requires arguments [ContainerName] or [SchemaName] [ContainerName]')
