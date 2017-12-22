from argparse import ArgumentParser
from collections import defaultdict

import json
import os
import common_module

from DependencyNode import DependencyNode

def main(dep_tree_dir, experiment_dir, url_filename, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    urls = get_urls(url_filename)
    for page_url in urls:
        print 'Processing: ' + page_url

        # Get the dependency relationship.
        atf_filename = os.path.join(experiment_dir, page_url, 'atf_content')
        raw_dependency_tree_filename = os.path.join(dep_tree_dir, page_url + '.json')
        if not (os.path.exists(atf_filename) and os.path.exists(raw_dependency_tree_filename)):
            print '\tfiles missing...'
            continue
        _, _, url_to_node = parse_dependency_tree(raw_dependency_tree_filename, page_url)

        # Get objects that are above the fold.
        atf_objects = parse_atf_map(atf_filename)

        url_to_parents = {}
        for url in atf_objects:
            if url not in url_to_node:
                continue
            url_to_parents[url] = []
            cur_node = url_to_node[url]
            while cur_node.parent != '':
                if common_module.escape_page(cur_node.url) != page_url:
                    url_to_parents[url].append(cur_node.url)

                if cur_node.parent not in url_to_node:
                    # Skip any node that are not in the dependency tree.
                    break
                cur_node = url_to_node[cur_node.parent]

        # Aggregate result.
        important_urls = set()
        for url, parents in url_to_parents.iteritems():
            for p in parents:
                important_urls.add(p)
        
        output_filename = os.path.join(output_dir, page_url)
        output_to_file(important_urls, output_filename)

def output_to_file(important_urls, output_filename):
    with open(output_filename, 'wb') as output_file:
        output_file.write('\n'.join(important_urls))

def get_urls(url_filename):
    urls = []
    with open(url_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip().split()
            urls.append(common_module.escape_page(l[1]))
    return urls

# Returns a dependency tree in the adjacency list format.
def parse_dependency_tree(dependency_tree_filename, page):
    tree = defaultdict(list)
    url_to_node = {}
    root_node = None
    with open(dependency_tree_filename, 'rb') as input_file:
        dependencies = json.loads(input_file.readline())
        for _, raw_node in dependencies.iteritems():
            node = DependencyNode()
            node.populate_node(raw_node)

            # Try to get the root_node
            if root_node == None and node.is_root and common_module.escape_page(node.url) == page:
                root_node = node

            # Add all nodes that have a parent.
            if node.parent != None:
                tree[node.parent].append(node)
            url_to_node[node.url] = node
    return tree, root_node, url_to_node

# Returns a mapping from resource URL to whether it appears above-the-fold or not.
def parse_atf_map(atf_map_filename):
    atf_objects = []
    with open(atf_map_filename, 'rb') as input_file:
        file_content = input_file.read()
        atf_map = json.loads(file_content)
        for url, is_atf in atf_map.iteritems():
            if is_atf:
                atf_objects.append(url)
    return atf_objects

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dep_tree_dir')
    parser.add_argument('experiment_dir')
    parser.add_argument('url_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.dep_tree_dir, args.experiment_dir, args.url_filename, args.output_dir)
