from jinja2 import Environment, FileSystemLoader
import os
import sys
from .util import snake_style

file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'generation_templates'))
env = Environment(loader=file_loader)

def generate_factory_headers(RS_subclass, base_class, RS_container):
    h_template = env.get_template('RS_factory_header_template.txt')
    factory_subclass = f'{RS_subclass}Factory'
    base_class_root_name = base_class[:-4] if base_class.endswith('Base') else base_class
    return h_template.render(include_guard=snake_style(factory_subclass).upper(), 
                             base_class_file_name=snake_style(base_class_root_name),
                             base_class_root_name=base_class_root_name,
                             factory_subclass=factory_subclass,
                             container=RS_container)

def generate_factory_source(RS_subclass, base_class, RS_container):
    factory_subclass = f'{RS_subclass}Factory'
    impl_template = env.get_template('RS_factory_impl_template.txt')
    base_class_root_name = base_class[:-4] if base_class.endswith('Base') else base_class
    return impl_template.render(factory_subclass=factory_subclass,
                                subclass=RS_subclass,
                                subclass_file=snake_style(RS_subclass),
                                base_class_root_name=base_class_root_name,
                                container=RS_container)

def generate_library_files(RS_list):
    lib_header_template = env.get_template('libtk205_header_template.txt')
    lib_header = lib_header_template.render(RS_list = RS_list)
    lib_impl_template = env.get_template('libtk205_impl_template.txt')
    lib_impl = lib_impl_template.render(RS_list = RS_list)
    return lib_header, lib_impl


if __name__ == '__main__':
    print(generate_factory_headers(sys.argv[1]))