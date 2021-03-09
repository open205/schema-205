from jinja2 import Environment, FileSystemLoader
import os
import sys

file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'src', 'templates'))
env = Environment(loader=file_loader)

def generate_factory_headers(RS_subclass, base_class, RS_container):
    h_template = env.get_template('RS_factory_header_template.txt')
    factory_subclass = f'{RS_subclass}_factory'
    base_class_root_name = base_class[:-5] if base_class.endswith('_base') else base_class
    return h_template.render(include_guard=factory_subclass.upper(), 
                             base_class_root_name=base_class_root_name,
                             factory_subclass=factory_subclass,
                             container=RS_container)

def generate_factory_source(RS_subclass, base_class, RS_container):
    factory_subclass = f'{RS_subclass}_factory'
    impl_template = env.get_template('RS_factory_impl_template.txt')
    base_class_root_name = base_class[:-5] if base_class.endswith('_base') else base_class
    return impl_template.render(factory_subclass=factory_subclass, 
                                subclass=RS_subclass,
                                base_class_root_name=base_class_root_name,
                                container=RS_container)

if __name__ == '__main__':
    print(generate_factory_headers(sys.argv[1]))