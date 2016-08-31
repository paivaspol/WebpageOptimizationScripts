from argparse import ArgumentParser
from urlparse import urlparse

import os
import simplejson as json

def main(dependency_tree_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    files = os.listdir(dependency_tree_dir)
    for filename in files:
        page = extract_page(filename)
        dependency_file_path = os.path.join(dependency_tree_dir, filename)
        common_resources = None
        if args.common_resource_dir is not None:
            common_resources = get_common_resources(args.common_resource_dir, page)

        output_filename = os.path.join(output_dir, page)
        result = generate_javascript_to_children_mapping(dependency_file_path, common_resources)
        with open(output_filename, 'wb') as output_file:
            output_file.write(json.dumps(result))

def generate_javascript_to_children_mapping(dependency_filename, common_resources):
    result = dict()
    with open(dependency_filename, 'rb') as input_file:
        dependency_tree_object = json.load(input_file)
        for resource_url in dependency_tree_object:
            parsed_url = urlparse(resource_url)
            if parsed_url.path.endswith('.js') and not resource_url.startswith('data'):
                if common_resources is None or resource_url in common_resources:
                    node = dependency_tree_object[resource_url]
                    children = [ x for x in node['children'] if not x.startswith('data') ]
                    if len(children) > 0:
                        result[resource_url] = children
    return result

def extract_page(filename):
    return filename[:len(filename) - len('.json')]

def get_common_resources(common_resource_dir, page):
    common_resource_filename = os.path.join(common_resource_dir, page)
    with open(common_resource_filename, 'rb') as input_file:
        return { line.strip() for line in input_file }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependency_tree_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--common-resource-dir', default=None)
    args = parser.parse_args()
    main(args.dependency_tree_dir, args.output_dir)
