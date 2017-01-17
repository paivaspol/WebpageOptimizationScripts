from argparse import ArgumentParser

import common_module
import os

def main(first_dependency_dir, second_dependency_dir, page_list_filename, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = get_page_list(page_list_filename)
    for page in pages:
        first_dependency_file = os.path.join(first_dependency_dir, page, 'dependency_tree.txt')
        second_dependency_file = os.path.join(second_dependency_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(first_dependency_file) and os.path.exists(second_dependency_file)):
            continue
        first_file_dependencies, first_url_type = get_dependencies(first_dependency_file)
        second_file_dependencies, second_url_type = get_dependencies(second_dependency_file)
        intersection = first_file_dependencies & second_file_dependencies
        union = first_file_dependencies | second_file_dependencies
        difference = union - intersection
        first_url_type.update(second_url_type)
        output_to_file(output_dir, page, difference, first_url_type)

def output_to_file(output_dir, page, result, url_type):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for entry in result:
            if url_type[entry] == 'DEFAULT':
                output_file.write(entry + ' ' + url_type[entry] + '\n')

def get_dependencies(dependency_filename):
    with open(dependency_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        url_to_type = { entry[2]: entry[4] for entry in temp }
        url_set = { entry[2] for entry in temp }
        return url_set, url_to_type 

def get_page_list(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ common_module.escape_url(entry[len(entry) - 1]) for entry in temp ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_dependency_root_dir')
    parser.add_argument('second_dependency_root_dir')
    parser.add_argument('page_list_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.first_dependency_root_dir, args.second_dependency_root_dir, args.page_list_filename, args.output_dir)
