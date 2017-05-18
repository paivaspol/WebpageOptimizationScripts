from argparse import ArgumentParser

import json
import os

def main(root_dir, dependency_dir):
    for p in os.listdir(root_dir):
        timing_filename = os.path.join(root_dir, p, 'timings.txt')
        dependency_filename = os.path.join(dependency_dir, p, 'dependency_tree.txt')
        if not (os.path.exists(timing_filename) and os.path.exists(dependency_filename)):
            continue
        dependencies = get_dependencies(dependency_filename)
        counter = 0
        with open(timing_filename, 'rb') as input_file:
            for l in input_file:
                timing = json.loads(l.strip())
                url = timing['url']
                if url in dependencies and timing['preloaded'] and timing['discovery_time'] == -1:
                    counter += 1
            if counter > 0:
                print p + ' ' + str(counter)

def get_dependencies(dependency_filename):
    dependencies = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            dependencies.add(raw_line.strip().split()[2])
    return dependencies

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir', help='The extended waterfall json directory')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)

