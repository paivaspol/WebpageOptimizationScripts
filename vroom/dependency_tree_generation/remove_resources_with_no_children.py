from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os

def main(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        dependency_filename = os.path.join(root_dir, page, 'dependency_tree.txt')
        output_filename = os.path.join(output_dir, page, 'dependency_tree.txt')
        common_module.create_directory_if_not_exists(os.path.join(output_dir, page))
        with open(dependency_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                parsed_url = urlparse(line[2])
                if (parsed_url.path.endswith('.css') or \
                    parsed_url.path.endswith('.js') or \
                    parsed_url.path.endswith('.html')):
                    output_file.write(raw_line)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
