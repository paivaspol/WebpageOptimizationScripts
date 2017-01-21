from argparse import ArgumentParser

import os

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        dep_filename = os.path.join(root_dir, page, 'dependency_tree.txt')
        if not os.path.exists(dep_filename):
            continue
        fraction = find_fraction(dep_filename)
        print '{0} {1}'.format(page, fraction)

def find_fraction(dep_filename):
    total_lines = 0
    xhr_count = 0
    with open(dep_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            res_type = line[4]
            total_lines += 1
            if res_type == 'XHR':
                xhr_count += 1
    return 1.0 * xhr_count / total_lines

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
