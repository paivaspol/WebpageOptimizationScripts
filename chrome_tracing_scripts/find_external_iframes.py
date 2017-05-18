from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

from DependencyNode import DependencyNode

import common_module
import json
import os

def find_descendants_of_iframes(dependency_tree, cur_node, page, result):
    children = dependency_tree[cur_node.url]
    # print 'root: {0} children {1}'.format(cur_node.url, children)
    for child in children:
        parsed_url = urlparse(child.url)
        if child.type == 'Document' and parsed_url.netloc != page:
            result.add(child.url)
        find_descendants_of_iframes(dependency_tree, child, page, result)

def parse_dependency_tree(dependency_tree_filename, page):
    tree = defaultdict(list)
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
    return tree, root_node

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    for f in os.listdir(args.dependency_dir):
        page = common_module.remove_json(f)
        tree, root_node = parse_dependency_tree(os.path.join(args.dependency_dir, f), page)
        result = set()
        if root_node is not None:
            find_descendants_of_iframes(tree, root_node, page, result)
            print page + ' ' + str(len(result))
            # for r in result:
            #     print '\t' + r
