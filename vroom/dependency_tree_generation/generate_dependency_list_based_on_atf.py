from argparse import ArgumentParser

import os
import common_module

def main(dependency_dir, important_dependencies_dir, urls_filename, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    urls = get_urls(urls_filename)
    for url in urls:
        important_dependencies_filename = os.path.join(important_dependencies_dir, url)
        dependency_list_filename = os.path.join(dependency_dir, url, 'dependency_tree.txt')
        if not (os.path.exists(important_dependencies_filename) and os.path.exists(dependency_list_filename)):
            continue
        important_dependencies = parse_important_dependencies(important_dependencies_filename)
        dependencies = parse_dependency_list_file(dependency_list_filename)
        result = []
        for dependency in dependencies:
            dep_url = dependency[2]
            resource_type = dependency[4]
            if (dep_url in important_dependencies or resource_type == 'Stylesheet') or not args.ignore_non_atf:
                dependency = change_vroom_priority(important_dependencies, dependency)
                result.append(dependency)
        page_output_dir = os.path.join(output_dir, url)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)
        output_to_file(result, os.path.join(page_output_dir, 'dependency_tree.txt'))

def output_to_file(dependencies, output_filename):
    with open(output_filename, 'wb') as output_file:
        for d in dependencies:
            output_file.write(' '.join(list(d)) + '\n')

def parse_important_dependencies(important_dependencies_filename):
    result = set()
    with open(important_dependencies_filename, 'rb') as input_file:
        for l in input_file:
            result.add(l.strip())
    return result

def change_vroom_priority(important_dependencies, dependency):
    dep_url = dependency[2]
    resource_type = dependency[4]
    # if dep_url in important_dependencies and dependency[4] != 'Image':
    #     return (dependency[0], dependency[1], dependency[2], dependency[3], \
    #             dependency[4], dependency[5], 'Important')
    # elif dep_url in important_dependencies and dependency[4] == 'Image':
    #     return (dependency[0], dependency[1], dependency[2], dependency[3], \
    #             dependency[4], dependency[5], 'Semi-important')
    if dep_url in important_dependencies:
        return (dependency[0], dependency[1], dependency[2], dependency[3], \
                dependency[4], dependency[5], 'Important')
    elif resource_type == 'Stylesheet':
        # Make sure that stylesheets are always important.
        return (dependency[0], dependency[1], dependency[2], dependency[3], \
                dependency[4], dependency[5], 'Important')
    elif not args.ignore_non_atf and args.push_down_important and dependency[6] == 'Important':
        return (dependency[0], dependency[1], dependency[2], dependency[3], \
                dependency[4], dependency[5], 'Semi-important')
    return dependency

def parse_dependency_list_file(dependency_list_filename):
    result = []
    with open(dependency_list_filename, 'r') as input_file:
        for l in input_file:
            result.append(l.strip().split())
    return result

def get_urls(url_filename):
    urls = []
    with open(url_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip().split()
            urls.append(common_module.escape_url(l[1]))
    return urls

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependency_dir')
    parser.add_argument('important_dependencies_dir')
    parser.add_argument('url_filename')
    parser.add_argument('output_dir')
    parser.add_argument('--push-down-important', default=False, action='store_true')
    parser.add_argument('--ignore-non-atf', default=False, action='store_true')
    args = parser.parse_args()
    main(args.dependency_dir, args.important_dependencies_dir, args.url_filename, args.output_dir)
