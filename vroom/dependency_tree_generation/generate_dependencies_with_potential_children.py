from argparse import ArgumentParser
from urlparse import urlparse

import os

def main(dependencies_for_proxy_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = os.listdir(dependencies_for_proxy_dir)
    for page in pages:
        dependency_filename = os.path.join(dependencies_for_proxy_dir, page, 'dependency_tree.txt')
        dependency_lines = get_dependencies_with_potential_children(dependency_filename)
        output_to_file(output_dir, page, dependency_lines)

def output_to_file(output_dir, page, dependency_lines):
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))

    output_path = os.path.join(output_dir, page, 'dependency_tree.txt')
    with open(output_path, 'wb') as output_file:
        for dependency_line in dependency_lines:
            output_file.write(dependency_line)

def get_dependencies_with_potential_children(dependency_filename):
    lines = []
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            resource_type = line[4]
            if resource_type == 'Document' or \
                resource_type == 'Script' or \
                resource_type == 'Stylesheet':
                lines.append(raw_line)
    return lines

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependencies_for_proxy_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.dependencies_for_proxy_dir, args.output_dir)
