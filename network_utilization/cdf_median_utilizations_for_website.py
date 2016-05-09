from argparse import ArgumentParser

import os
import numpy

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        process_page(root_dir, page)

def process_page(root_dir, page):
    utilizations_filename = os.path.join(root_dir, page, 'utilizations.txt')
    utilizations = []
    with open(utilizations_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            utilization = float(line[1])
            utilizations.append(utilization)
    if len(utilizations) > 0:
        median = numpy.median(utilizations)
        print '{0} {1}'.format(page, median)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    process_pages(args.root_dir)
