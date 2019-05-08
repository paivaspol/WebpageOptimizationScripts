from argparse import ArgumentParser

import os
import simplejson as json

import common_module

JSON_SUFFIX = '.json'

def generate_dependencies_for_proxy(root_dir, pages, output_dir):
    if args.use_non_redirect:
        non_redirected_url = common_module.get_pages(args.pages_file, index=0)

    for i in range(0, len(pages)):
        page = pages[i]
        if 'money.cnn.com' in page or 'nba.com' in page:
            continue
        url = common_module.escape_url(page)
        dependency_tree_path = os.path.join(root_dir, common_module.escape_url(page) + ".json")
        print 'path: ' + dependency_tree_path + ' url: ' + url
        if url == 'cnn.com' or url == 'money.cnn.com' or url == 'nba.com':
            continue
        if args.use_non_redirect:
            generate_dependencies_for_proxy_main(dependency_tree_path, page, output_dir, non_redirected_url[i])
        else:
            generate_dependencies_for_proxy_main(dependency_tree_path, page, output_dir, None)

def generate_dependencies_for_proxy_main(dependency_tree_path, page, output_dir, non_redirect_url):
    if not os.path.exists(dependency_tree_path):
        return
    given_dependencies = None
    if args.use_only_given_dependencies != '':
        given_dependencies = get_given_dependencies(os.path.join(args.use_only_given_dependencies, common_module.escape_url(page)))

    result_dependencies = [] # A list containing dependency lines
    dependency_tree_object = get_dependency_objects(dependency_tree_path)
    generate_file_from_dependency_tree_object(dependency_tree_object, \
                                              page, page, page, \
                                              result_dependencies)
    if args.serve_from_outer_html:
        result_dependencies = change_origin_url(result_dependencies, page)
    result_dependencies.sort(key=lambda x: x[3])
    output_page = non_redirect_url if non_redirect_url is not None else page
    output_page = common_module.escape_url(output_page)
    output_to_file(result_dependencies, output_page, output_dir, given_dependencies)

def change_origin_url(result_dependencies, page):
    result = []
    for dependency in result_dependencies:
        entry = (page, dependency[1], dependency[2], dependency[3], dependency[4])
        result.append(entry)
    return result

def get_given_dependencies(given_dependencies_filename):
    retval = set()
    with open(given_dependencies_filename, 'rb') as input_file:
        for raw_line in input_file:
            retval.add(raw_line.strip())
    return retval

def output_to_file(result_dependencies, url, output_dir, given_dependencies):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    base_dir = os.path.join(output_dir, url)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    dependency_graph_filename = os.path.join(base_dir, 'dependency_tree.txt')
    with open(dependency_graph_filename, 'wb') as output_file:
        printed_line = set()
        for result_dependency in result_dependencies:
            origin_url = result_dependency[0]
            if not origin_url.endswith('/'):
                origin_url += '/'
            parent_url = result_dependency[1]
            if parent_url.endswith('.js') and parent_url.endswith('.css') and parent_url.endswith('.html') and not parent_url.endswith('/'):
                parent_url += '/'
            if given_dependencies is not None and result_dependency[2] not in given_dependencies:
                continue
            dependency_line = '{0} {1} {2} {3} {4}'.format(origin_url, parent_url, result_dependency[2], result_dependency[3], result_dependency[4])
            if dependency_line not in printed_line:
                output_file.write(dependency_line + '\n')
            printed_line.add(dependency_line)
 
def generate_file_from_dependency_tree_object(dependency_tree_object, \
                                              dependency_url, \
                                              parent_url, \
                                              origin_url, \
                                              result_dependencies):
    '''
    Recursive method for generating the dependency graph.
    '''
    if dependency_url == 'http://ec2-54-237-249-55.compute-1.amazonaws.com':
        dependency_url += '/'

    if dependency_url not in dependency_tree_object:
        print str(dependency_tree_object) + ' ' + dependency_url
        return

    dependency_node = dependency_tree_object[dependency_url]
    children = dependency_node['children']
    cur_domain = extract_domain(dependency_url)
    for child in children:
        child_found_index = dependency_tree_object[child]['found_index']
        resource_type = dependency_tree_object[child]['type'] if 'type' in dependency_tree_object[child] else 'DEFAULT'
        dependency_line = (origin_url, dependency_url, child, child_found_index, resource_type)
        result_dependencies.append(dependency_line)
        next_domain = extract_domain(child)
        # print 'current: {0} child: {1}'.format(dependency_url, child)
        # print 'origin_url: {0}'.format(origin_url)
        # print 'next domain: {0} current domain: {1}'.format(next_domain, cur_domain)
        # print ''
        next_origin_url = origin_url if next_domain == cur_domain else child
        # generate_file_from_dependency_tree_object(dependency_tree_object, \
        #                                            child, \
        #                                            dependency_url, \
        #                                            next_origin_url, \
        #                                            result_dependencies)
        try:
            if not generate_file_from_dependency_tree_object(dependency_tree_object, \
                                                       child, \
                                                       dependency_url, \
                                                       next_origin_url, \
                                                       result_dependencies):
                break
        except RuntimeError as e:
            # print str(e)
            return False
    return True

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
    index = result_url.find(url)
    return result_url[index : index + len(url)]

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
    parser.add_argument('--use-only-given-dependencies', default='')
    parser.add_argument('--use-non-redirect', default=False, action='store_true')
    parser.add_argument('--serve-from-outer-html', default=False, action='store_true')
    args = parser.parse_args()
    pages = common_module.get_pages(args.pages_file)
    generate_dependencies_for_proxy(args.root_dir, pages, args.output_dir)
