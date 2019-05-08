from argparse import ArgumentParser

import constants
import json
import os

def main(root_dir, dep_dir):
    for p in os.listdir(root_dir):
        network_filename = os.path.join(root_dir, p, 'network_' + p)
        dependency_filename = os.path.join(dep_dir, p, 'dependency_tree.txt')
        if not os.path.exists(network_filename) or \
            not os.path.exists(dependency_filename):
            continue
        resources = get_all_resources(network_filename)
        dependencies = get_all_deps(dependency_filename)
        fraction = 1.0 * len(dependencies) / len(resources)
        print '{0} {1} {2} {3}'.format(p, len(resources), len(dependencies), fraction)

def get_all_deps(deps_filename):
    deps = set()
    with open(deps_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            deps.add(line[2])
    return deps

def get_all_resources(network_filename):
    urls = set()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == 'Network.responseReceived':
                urls.add(network_event[constants.PARAMS][constants.RESPONSE][constants.URL])
    return urls

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dep_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dep_dir)
