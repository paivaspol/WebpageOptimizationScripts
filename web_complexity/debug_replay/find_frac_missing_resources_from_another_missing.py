from argparse import ArgumentParser
from anytree import find
from anytree.importer import JsonImporter

from multiprocessing import Pool

import os

def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    result_objects = []
    with Pool() as pool:
        for d in os.listdir(args.missing_resources_dir):
            missing_resources_filename = os.path.join(args.missing_resources_dir, d, 'missing')
            dependency_tree_filename = os.path.join(args.dependency_tree_dir, d)
            page_output_filename = os.path.join(args.output_dir, d)
            if not (os.path.exists(missing_resources_filename) and
                    os.path.exists(dependency_tree_filename)):
                continue

            result_obj = pool.apply_async(FindMissingUrlsFromAnotherMissingUrl, args=(d, missing_resources_filename,
                    dependency_tree_filename, page_output_filename))
            result_objects.append((d, result_obj))

        for pageurl, r in result_objects:
            print('{0} {1}'.format(pageurl, r.get()))


def ImportTree(dependency_tree_filename):
    '''Imports the tree from the given file and returns the root.'''
    importer = JsonImporter()
    with open(dependency_tree_filename, 'r') as input_file:
        file_content = input_file.read()
        return importer.import_(file_content)


def GetMissingResources(missing_resources_filename):
    '''Returns a set of missing resources.'''
    missing_resources = set()
    with open(missing_resources_filename, 'r') as input_file:
        for l in input_file:
            l = l.strip().split()
            missing_resources.add(l[0])
    return missing_resources


def NodeCheckHelper(node, missing_resources, urls_missing_from_another_missing):
    '''Helper for traversing the dependency tree.'''
    if node.name in urls_missing_from_another_missing:
        # We already have examined this resource and its subtree. no need to do it again.
        return

    node_children = node.children
    for child in node_children:
        if child.name in missing_resources:
            urls_missing_from_another_missing.add(child.name)
            NodeCheckHelper(
                    child, missing_resources, urls_missing_from_another_missing)


def FindMissingUrlsFromAnotherMissingUrl(pageurl, missing_resources_filename,
        dependency_tree_filename, output_filename):
    # print('Processing: {0}'.format(pageurl))
    root_node = ImportTree(dependency_tree_filename)
    missing_resources = GetMissingResources(missing_resources_filename)
    urls_missing_from_another_missing = set()
    for url in missing_resources:
        node = find(root_node, lambda node: node.name == url)
        if node is None:
            continue
        NodeCheckHelper(node, missing_resources, urls_missing_from_another_missing)
    with open(output_filename, 'w') as output_file:
        for url in urls_missing_from_another_missing:
            output_file.write(url + '\n')
    return len(urls_missing_from_another_missing)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('missing_resources_dir')
    parser.add_argument('dependency_tree_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
