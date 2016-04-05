from argparse import ArgumentParser

import os
import simplejson as json

import common_module

JSON_SUFFIX = '.json'

def generate_dependencies_for_proxy(root_dir, pages, output_dir):
    for page in pages:
        url = common_module.escape_url(page)
        path = os.path.join(root_dir, url)
        dependency_tree_path = os.path.join(path, "dependency_graph.json")
        print 'path: ' + dependency_tree_path + ' url: ' + url
        if not os.path.exists(dependency_tree_path):
            continue
        result_dependencies = [] # A list containing dependency lines
        dependency_tree_object = get_dependency_objects(dependency_tree_path)
        try:
            generate_file_from_dependency_tree_object(dependency_tree_object, \
                                                      page, page, page, \
                                                      result_dependencies)
        except RuntimeError as e:
            print str(e) + ' page: ' + page
            pass
        result_dependencies.sort(key=lambda x: x[3])
        output_to_file(result_dependencies, url, output_dir)

def output_to_file(result_dependencies, url, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    base_dir = os.path.join(output_dir, url)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    dependency_graph_filename = os.path.join(base_dir, 'dependency_tree.txt')
    with open(dependency_graph_filename, 'wb') as output_file:
        for result_dependency in result_dependencies:
            origin_url = result_dependency[0]
            if not origin_url.endswith('/'):
                origin_url += '/'
            parent_url = result_dependency[1]
            if not parent_url.endswith('/'):
                parent_url += '/'
            dependency_line = '{0} {1} {2} {3}'.format(origin_url, parent_url, result_dependency[2], result_dependency[3])
            output_file.write(dependency_line + '\n')
 
def generate_file_from_dependency_tree_object(dependency_tree_object, \
                                              dependency_url, \
                                              parent_url, \
                                              origin_url, \
                                              result_dependencies):
    '''
    Recursive method for generating the dependency graph.
    '''
    if dependency_url not in dependency_tree_object:
        return
    dependency_node = dependency_tree_object[dependency_url]
    children = dependency_node['children']
    if children is not None:
        for child in children:
            #print 'child: ' + child
            child_found_index = dependency_tree_object[child]['found_index']
            dependency_line = (origin_url, parent_url, child, child_found_index)
            result_dependencies.append(dependency_line)
            next_domain = extract_domain(dependency_url)
            generate_file_from_dependency_tree_object(dependency_tree_object, \
                                                       child, \
                                                       dependency_url, \
                                                       next_domain, \
                                                       result_dependencies)

def extract_domain(url):
    '''
    Extracts the domain from the url
    '''
    result_url = url
    if url.startswith(common_module.HTTPS_PREFIX):
        url = url[len(common_module.HTTPS_PREFIX):]
    elif url.startswith(common_module.HTTP_PREFIX):
        url = url[len(common_module.HTTP_PREFIX):]
    url = url[:url.find('/')]
    return result_url[:result_url.find(url) + len(url)]

def get_dependency_objects(filename):
    with open(filename, 'rb') as input_file:
        line = input_file.readline()
        dependency_tree_object = json.loads(line)
    return dependency_tree_object

def extract_url_from_filename(filename):
    return filename[:len(filename) - len(JSON_SUFFIX)]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_file')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    pages = common_module.get_pages(args.pages_file)
    generate_dependencies_for_proxy(args.root_dir, pages, args.output_dir)
