from argparse import ArgumentParser

import os

def main(first_root_dir, second_root_dir):
    first_directory_resources = get_resources(first_root_dir)
    second_directory_resources = get_resources(second_root_dir)
    for page in first_directory_resources:
        if page in second_directory_resources and len(first_directory_resources[page] - second_directory_resources[page]) > 0:
            print '{0} first_dir: {1} second_dir: {2} diff: {3}'.format(page, len(first_directory_resources[page]), len(second_directory_resources[page]), len(first_directory_resources[page] - second_directory_resources[page]))

def get_resources(root_dir):
    result = dict()
    pages = os.listdir(root_dir)
    for page in pages:
        resources = set()
        resources_filename = os.path.join(root_dir, page, 'html_children.txt')
        if not os.path.exists(resources_filename):
            continue
        with open(resources_filename, 'rb') as input_file:
            for raw_line in input_file:
                resources.add(raw_line.strip())
        result[page] = resources
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_root_dir')
    parser.add_argument('second_root_dir')
    args = parser.parse_args()
    main(args.first_root_dir, args.second_root_dir)

