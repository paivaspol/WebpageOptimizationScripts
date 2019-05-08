from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(dependency_tree_dir, domain_depth_with_url_filename, output_dir):
    page_to_domain_depth_and_url_dict = get_domain_depth_with_url(domain_depth_with_url_filename)
    common_module.create_directory_if_not_exists(output_dir)
    for page in page_to_domain_depth_and_url_dict:
        domain_depth_and_url = page_to_domain_depth_and_url_dict[page]
        dependency_tree_filename = os.path.join(dependency_tree_dir, page + '.json')
        dependency_tree_object = get_dependency_tree_object(dependency_tree_filename)
        critical_domain_depth_path = find_critical_path(domain_depth_and_url[1], dependency_tree_object)
        output_filename = os.path.join(output_dir, page)
        print page + ' Expected: {0} Actual: {1}'.format(domain_depth_and_url[0], len(critical_domain_depth_path))
        output_to_file(critical_domain_depth_path, domain_depth_and_url[0], output_filename)

def output_to_file(critical_path, domain_depth, output_filename):
    with open(output_filename, 'wb') as output_file:
        for node in critical_path:
            output_file.write(node + '\n')

def find_critical_path(last_url, dependency_tree):
    chain = []
    cur_node = dependency_tree[last_url]
    while not cur_node['isRoot']:
        chain.insert(0, cur_node['url'])
        parent = cur_node['parent']
        cur_node = dependency_tree[parent]
        if cur_node['isRoot']:
            chain.insert(0, cur_node['url'])
    return chain

def get_dependency_tree_object(dependency_tree_filename):
    with open(dependency_tree_filename, 'rb') as input_file:
        return json.load(input_file)

def get_domain_depth_with_url(domain_depth_with_url_filename):
    result = dict()
    with open(domain_depth_with_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            page, domain_depth, url = raw_line.strip().split()
            result[page] = (domain_depth, url)
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependency_tree_dir')
    parser.add_argument('domain_depth_with_url_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.dependency_tree_dir, args.domain_depth_with_url_filename, args.output_dir)
