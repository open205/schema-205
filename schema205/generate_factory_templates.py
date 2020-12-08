from jinja2 import Environment, FileSystemLoader
import os
import sys

file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'src', 'templates'))
env = Environment(loader=file_loader)

def generate_factory_headers(RS_subclass):
    h_template = env.get_template('RS_factory_header_template.txt')
    factory_subclass = f'{RS_subclass}_factory'
    return h_template.render(include_guard=factory_subclass.upper(), factory_subclass=factory_subclass)

def generate_factory_source(RS_subclass):
    factory_subclass = f'{RS_subclass}_factory'
    impl_template = env.get_template('RS_factory_impl_template.txt')
    return impl_template.render(factory_subclass=factory_subclass, RS_subclass=RS_subclass)

if __name__ == '__main__':
    print(generate_factory_headers(sys.argv[1]))