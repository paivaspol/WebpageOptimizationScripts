from argparse import ArgumentParser
from collections import defaultdict

import common_module
import os

def main(page, timing_filename, dependency_filename):
    preload_timings = common_module.get_preloaded_timings(timing_filename)
    dep_cat_map = get_dependencies_category_map(dependency_filename)

    result = { 'Important': -1, 'Semi-important': -1, 'Unimportant': -1 }
    found_cat_set = set()
    for obj in preload_timings:
        url, discovery_time, net_wait_time, preload_discovery, _ = obj
        found_cat = None
        for cat in dep_cat_map:
            if url in dep_cat_map[cat] and \
                cat not in found_cat_set:
                result[cat] = preload_discovery
                found_cat = cat
                break
        found_cat_set.add(found_cat)
        if len(found_cat_set) == 3:
            break

    if result['Unimportant'] == -1:
        for obj in preload_timings:
            url, _, _, _, resource_finish = obj
            if url in dep_cat_map['Semi-important']:
                result['Unimportant'] = max(resource_finish, result['Semi-important'])

    output_line = page
    output_line += ' ' + str(result['Important'])
    output_line += ' ' + str(result['Semi-important'])
    output_line += ' ' + str(result['Unimportant'])
    print output_line

def get_dependencies_category_map(dependency_filename):
    result = defaultdict(set)
    with open(dependency_filename, 'rb') as input_file:
        for line in input_file:
            line = line.strip().split()
            url = line[2]
            dep_type = line[-1]
            result[dep_type].add(url)
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    for p in os.listdir(args.root_dir):
        timing_filename = os.path.join(args.root_dir, p, 'timings.txt')
        dependency_filename = os.path.join(args.dependency_dir, p, 'dependency_tree.txt')
        if not (os.path.exists(timing_filename) and \
                os.path.exists(dependency_filename)):
            continue
        main(p, timing_filename, dependency_filename)
