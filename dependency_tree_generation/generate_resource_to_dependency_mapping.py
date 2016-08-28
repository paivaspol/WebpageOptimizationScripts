from argparse import ArgumentParser

import os
import simplejson as json

def main(dependency_tree_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    files = os.listdir(dependency_tree_dir)
    for filename  in files:
        page = extract_page(filename)
        dependency_file_path = os.path.join(dependency_tree_dir, filename)
        output_filename = os.path.join(output_dir, page)
        result = generate_javascript_to_children_mapping(dependency_file_path)
        with open(output_filename, 'wb') as output_file:
            output_file.write(json.dumps(result))

def generate_javascript_to_children_mapping(dependency_filename):
    result = dict()
    with open(dependency_filename, 'rb') as input_file:
        dependency_tree_object = json.load(input_file)
        for resource_url in dependency_tree_object:
            if not resource_url.startswith('data'):
                node = dependency_tree_object[resource_url]
                children = [ x for x in node['children'] if not x.startswith('data') ]
                if len(children) > 0:
                    result[resource_url] = children
    return result

def extract_page(filename):
    return filename[:len(filename) - len('.json')]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependency_tree_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.dependency_tree_dir, args.output_dir)
