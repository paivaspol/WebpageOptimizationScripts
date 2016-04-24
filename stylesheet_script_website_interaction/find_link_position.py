from argparse import ArgumentParser

import os
import numpy

def process_files(root_dir):
    for directory in os.listdir(root_dir):
        base_dir = os.path.join(root_dir, directory)
        original_html_filename = os.path.join(base_dir, 'before_page_load.html')
        if not os.path.exists(original_html_filename):
            continue
        locations, total_lines = find_link_locations(original_html_filename)
        if len(locations) > 0:
            mean = numpy.mean(locations)
            median = numpy.median(locations)
            relative_mean = 1.0 * mean / total_lines
            relative_median = 1.0 * median / total_lines
            print '{0} {1} {2} {3} {4}'.format(directory, mean, median, relative_mean, relative_median)

def find_link_locations(original_html_filename):
    result = []
    with open(original_html_filename, 'rb') as input_file:
        for i, raw_line in enumerate(input_file):
            line = raw_line.strip()
            if line.startswith('<link'):
                # Just some santiy check
                if 'stylesheet' in line and \
                        'css' in line:
                    # print line
                    result.append(i)
    return result, i - 1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    process_files(args.root_dir)
