from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import os

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        if 'shutterstock.com' not in page:
            continue
        print 'Processing: ' + page
        dependency_tree_filename = os.path.join(root_dir, page, 'dependency_tree.txt')
        if not os.path.exists(dependency_tree_filename):
            continue
        dependency_tree, node_info, root_node_url = generate_dependency_tree(dependency_tree_filename, page)
        root_node = dependency_tree[root_node_url]
        depth = bfs(root_node, dependency_tree, node_info, root_node_url, 1)

def bfs(current_node, dependency_tree, node_info, current_node_url, depth):
    if len(current_node) == 0:
        return depth
    else:
        print '{0} {1} {2}'.format(node_info.keys(), current_node_url, current_node)
        return -1
        domain, parent, url = node_info[current_node_url]
        parsed_url = urlparse(url)
        return_depth = depth
        for child in current_node:
            if not child.startswith('data'):
                parsed_child_url = urlparse(child)
                next_depth = depth + 1 if parsed_child_url.netloc != parsed_url.netloc else depth
                return_depth = max(return_depth, bfs(dependency_tree[child], dependency_tree, node_info, child, next_depth))
        return return_depth

def generate_dependency_tree(dependency_tree_filename, page):
    node_info = dict()
    dependency_tree = defaultdict(list)
    root_node = None
    with open(dependency_tree_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            domain = line[0]
            parent = remove_trailing_slash(line[1])
            url = line[2]
            node_info[url] = (domain, parent, url)
            dependency_tree[parent].append(url)
            print 'url: {0} page: {1}'.format(url, page)
            if page == common_module.escape_url(url):
                root_node = url
    print 'root_node: {0}'.format(root_node)
    return dependency_tree, node_info, root_node

def remove_trailing_slash(url):
    while url.endswith('/'):
        url = url[:len(url) - 1]
    return url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
