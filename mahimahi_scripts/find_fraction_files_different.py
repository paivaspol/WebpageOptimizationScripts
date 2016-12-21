from argparse import ArgumentParser

import filecmp
import os

def main(first_dir, second_dir):
    pages = os.listdir(first_dir)
    for page in pages:
        first_page_dir = os.path.join(first_dir, page)
        second_page_dir = os.path.join(second_dir, page)
        fraction = find_fraction(first_page_dir, second_page_dir)
        print '{0} {1}'.format(page, fraction)

def find_fraction(first_dir, second_dir):
    first_dir_files = os.listdir(first_dir)
    second_dir_files = os.listdir(second_dir)
    matched_count = 0
    for first_dir_file in first_dir_files:
        path_to_first_dir_file = os.path.join(first_dir, first_dir_file)
        matched = False
        for second_dir_file in second_dir_files:
            path_to_second_dir_file = os.path.join(second_dir, second_dir_file)
            if filecmp.cmp(path_to_first_dir_file, path_to_second_dir_file):
                matched = True
                break
        if matched:
            matched_count += 1
    fraction = 1.0 * matched_count / len(first_dir_files)
    return fraction

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_dir')
    parser.add_argument('second_dir')
    args = parser.parse_args()
    main(args.first_dir, args.second_dir)
