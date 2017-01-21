from argparse import ArgumentParser
from collections import defaultdict

import common_module
import os
import sys

def main(root_dir, page_list, dependencies_dir):
    pages = common_module.get_pages(page_list)
    for page in pages:
        fetch_time_filename = os.path.join(root_dir, 'extended_waterfall', page, 'ResourceFinish.txt')
        processing_time_filename = os.path.join(root_dir, 'extended_waterfall', page, 'processing_time.txt')
        dependency_filename = os.path.join(dependencies_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(fetch_time_filename) and \
            os.path.exists(processing_time_filename) and \
            os.path.exists(dependency_filename)):
            continue
        # if 'news.google.com' not in page:
        #     continue
        dependencies = get_dependencies(dependency_filename)
        fetch_times = get_fetch_times(fetch_time_filename)
        end_processing_times = get_end_processing_times(processing_time_filename)

        # print dependencies
        # print fetch_times
        # print end_processing_times

        # For each page, we need to find the max of each dependent resource.
        max_time = find_max_of_processing_and_network(dependencies, fetch_times, end_processing_times)
        print '{0} {1}'.format(page, max_time)

def find_max_of_processing_and_network(dependencies, fetch_times, end_processing_times):
    max_time = -1
    for dep in dependencies:
        max_time = max(fetch_times[dep], end_processing_times[dep])
    return max_time / 1000.0 # convert to ms

def get_fetch_times(fetch_time_filename):
    result = defaultdict(lambda: -1)
    with open(fetch_time_filename,'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            try:
                result[line[0]] = max(int(line[2]), result[line[0]])
            except:
                pass
    return result

def get_end_processing_times(processing_time_filename):
    result = defaultdict(lambda: -1)
    with open(processing_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            try:
                result[line[0]] = max(int(line[3]), result[line[0]])
            except:
                pass
    return result

def get_dependencies(dependency_filename):
    result = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.add(line[2])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('dependencies_dir')
    args = parser.parse_args()
    main(args.root_dir, args.page_list, args.dependencies_dir)
