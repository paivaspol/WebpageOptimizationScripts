from argparse import ArgumentParser

import common_module
import os
import numpy

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = filter_page_not_on_page_list(pages, args.page_list)
    for page in pages:
        process_page(root_dir, page)

def filter_page_not_on_page_list(pages, page_list):
    pages_set = set(pages)
    with open(page_list, 'rb') as input_file:
        wanted_pages = set()
        for raw_line in input_file:
            escaped_page = common_module.escape_page(raw_line.strip().split()[1])
            wanted_pages.add(escaped_page)
        return pages_set & wanted_pages

def process_page(root_dir, page):
    page_path = os.path.join(root_dir, page)
    cpu_running_chrome_filename = os.path.join(page_path, 'cpu_running_chrome.txt')
    cpu_running_chrome = get_cpu_running_chrome(cpu_running_chrome_filename)
    cpu_utilization_filename = os.path.join(page_path, 'cpu_{0}_usage.txt'.format(cpu_running_chrome))
    utilizations = []
    with open(cpu_utilization_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            utilization = float(line[1])
            utilizations.append(utilization)
    if len(utilizations) > 0:
        median_utilization = numpy.median(utilizations)
        max_utilization = max(utilizations)
        min_utilization = min(utilizations)
        print '{0} {1} {2} {3}'.format(page, median_utilization, min_utilization, max_utilization)

def get_cpu_running_chrome(cpu_running_chrome_filename):
    with open(cpu_running_chrome_filename, 'rb') as input_file:
        return int(input_file.readline())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
