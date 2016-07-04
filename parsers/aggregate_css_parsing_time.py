from argparse import ArgumentParser

import os

def main(root_dir):
    pages = os.listdir(root_dir)
    parsing_times = []
    for page in pages:
        css_parsing_runtime_filename = os.path.join(root_dir, page, 'css_parsing_runtime.txt')
        if not os.path.exists(css_parsing_runtime_filename):
            continue
        with open(css_parsing_runtime_filename, 'rb') as input_file:
            for raw_line in input_file:
                parsing_times.append(float(raw_line.strip()))
    sorted_parsing_times = sorted(parsing_times)
    for parsing_time in sorted_parsing_times:
        print parsing_time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
