from argparse import ArgumentParser

import os

def main(root_dir, dependency_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        requests_filename = os.path.join(root_dir, page, 'ResourceSendRequest.txt')
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(requests_filename) and \
                os.path.exists(dependency_filename)):
            continue
        deps = get_dependencies(dependency_filename)
        requests = get_requests(requests_filename)
        dynamic = requests - deps
        output_to_file(output_dir, page, dynamic)

def output_to_file(output_dir, page, dynamic_resources):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for r in dynamic_resources:
            output_file.write(r + '\n')

def get_dependencies(dependency_filename):
    retval = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            retval.add(line[2])
    return retval

def get_requests(requests_filename):
    retval = set()
    with open(requests_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            retval.add(line[0])
    return retval

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir, args.output_dir)
