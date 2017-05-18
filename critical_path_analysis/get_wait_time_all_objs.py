from argparse import ArgumentParser

import common_module
import json
import os

def write_to_file(output_filename, result):
    with open(output_filename, 'wb') as output_file:
        for url, discovery, net_wait_time, _, _ in result:
            line = url + '\t' + str(discovery) + '\t' + str(net_wait_time)
            output_file.write(line + '\n')

def get_dependencies(dependency_filename):
    dependencies = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            dependencies.add(line[2])
    return dependencies

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    for p in os.listdir(args.root_dir):
        timing_filename = os.path.join(args.root_dir, p, 'timings.txt')
        dependency_filename = os.path.join(args.dependency_dir, p, 'dependency_tree.txt')
        if not (os.path.exists(timing_filename) and os.path.exists(dependency_filename)):
            continue
        dependencies = get_dependencies(dependency_filename)
        result = common_module.get_preloaded_timings(timing_filename)
        hinted_preloaded_output_dir = os.path.join(args.output_dir, 'hinted_and_preloaded')
        hinted_not_preloaded_output_dir = os.path.join(args.output_dir, 'hinted_but_not_preloaded')
        if not os.path.exists(hinted_preloaded_output_dir):
            os.mkdir(hinted_preloaded_output_dir)
            os.mkdir(hinted_not_preloaded_output_dir)

        result_not_preloaded_but_hinted = common_module.get_not_preloaded_but_hinted(timing_filename, dependencies)
        write_to_file(os.path.join(hinted_preloaded_output_dir, p), result)
        write_to_file(os.path.join(hinted_not_preloaded_output_dir, p), result_not_preloaded_but_hinted)

