from argparse import ArgumentParser

import common_module
import os

def main(extended_waterfall_dir, page_list, dependency_dir):
    pages = get_page_list(page_list)
    for page_tuple in pages:
        page, r_page = page_tuple
        request_filename = os.path.join(extended_waterfall_dir, page, 'ResourceSendRequest.txt') 
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(request_filename) and os.path.exists(dependency_filename)):
            continue
        dependencies = get_dependencies(dependency_filename)
        dynamic_resources, all_request_count = get_requests(request_filename, dependencies, r_page)
        fraction = 1.0 * len(dynamic_resources) / all_request_count
        print '{0} {1} {2} {3}'.format(page, len(dynamic_resources), all_request_count, fraction)

def get_requests(request_filename, dependencies, r_page):
    result = set()
    all_request_count = 0
    with open(request_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            all_request_count += 1
            url = line[0]
            if url not in dependencies and common_module.escape_page(url) != r_page:
                result.add(url)
    return result, all_request_count

def get_dependencies(dependency_filename):
    deps = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            deps.add(line[2])
    return deps

def get_page_list(page_list_filename):
    page_list = []
    with open(page_list_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            page_list.append( (common_module.escape_page(line[0]), common_module.escape_page(line[1])) )
    return page_list

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('extended_waterfall_dir')
    parser.add_argument('page_list')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.extended_waterfall_dir, args.page_list, args.dependency_dir)
