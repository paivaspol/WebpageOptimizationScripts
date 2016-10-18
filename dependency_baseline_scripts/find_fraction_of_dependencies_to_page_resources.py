from argparse import ArgumentParser

import common_module
import os

def main(dependencies_dir, all_resources_dir):
    pages = os.listdir(dependencies_dir)
    resource_pages = os.listdir(all_resources_dir)
    for page in pages:
        # if 'news.google.com' not in page:
        #     continue
        dependency_filename = os.path.join(dependencies_dir, page, 'dependency_tree.txt')
        page_resource_filename = os.path.join(all_resources_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(dependency_filename) and \
                os.path.exists(page_resource_filename)):
            continue
        get_fraction(dependency_filename, page_resource_filename, page)

def get_fraction(dependency_filename, page_resource_filename, page):
    dependencies = get_urls_and_types(dependency_filename, page)
    page_resources = get_urls_and_types(page_resource_filename, page)
    missing_resources = page_resources - dependencies
    miss_fraction = 1.0 * len(missing_resources) / len(page_resources)
    print '{0} {1}'.format(page, miss_fraction)
    if args.output_missing_dependencies:
        if not os.path.exists(args.output_missing_dependencies):
            os.mkdir(args.output_missing_dependencies)
        output_missing_dependencies(args.output_missing_dependencies, page, missing_resources)

def output_missing_dependencies(output_dir, page, missed_resources):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for missed_resource in missed_resources:
            output_file.write(missed_resource[0] + '\n')

def get_urls_and_types(resource_filename, page):
    results = set()
    with open(resource_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[2].strip()
            resource_type = line[4]
            if not url.startswith('data') and \
                common_module.escape_page(url) != page and \
                (not args.only_important_resources or \
                    (args.only_important_resources and \
                        (resource_type == 'Document' or \
                        resource_type == 'Script' or \
                        resource_type == 'Stylesheet'))):
                results.add((url, resource_type))
    return results

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependencies_dir')
    parser.add_argument('all_resources_dir')
    parser.add_argument('--only-important-resources', default=False, action='store_true')
    parser.add_argument('--output-missing-dependencies', default=None)
    args = parser.parse_args()
    main(args.dependencies_dir, args.all_resources_dir)
