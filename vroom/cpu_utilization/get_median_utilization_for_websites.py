from argparse import ArgumentParser

import common_module
import os
import numpy

def process_pages(root_dir, start_time_offset_dict, end_time_offset_dict):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = filter_page_not_on_page_list(pages, args.page_list)
    for page in pages:
        process_page(root_dir, page, start_time_offset_dict, end_time_offset_dict)

def filter_page_not_on_page_list(pages, page_list):
    pages_set = set(pages)
    with open(page_list, 'rb') as input_file:
        wanted_pages = set()
        for raw_line in input_file:
            escaped_page = common_module.escape_page(raw_line.strip().split()[1])
            wanted_pages.add(escaped_page)
        return pages_set & wanted_pages

def process_page(root_dir, page, start_time_offset_dict, end_time_offset_dict):
    page_path = os.path.join(root_dir, page)
    cpu_running_chrome_filename = os.path.join(page_path, 'cpu_running_chrome.txt')
    cpu_running_chrome = get_cpu_running_chrome(cpu_running_chrome_filename)
    cpu_utilization_filename = os.path.join(page_path, 'cpu_{0}_usage.txt'.format(cpu_running_chrome))
    utilizations = []
    start_time_offset = -1 if page not in start_time_offset_dict else start_time_offset_dict[page]
    end_time_offset = -1 if page not in end_time_offset_dict else end_time_offset_dict[page]
    with open(cpu_utilization_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            timestamp = float(line[0])
            if (start_time_offset != -1 and timestamp < start_time_offset) or \
                (end_time_offset != -1 and timestamp > end_time_offset):
                continue
            utilization = float(line[1])
            utilizations.append(utilization)
    if len(utilizations) > 0:
        median_utilization = numpy.average(utilizations)
        max_utilization = max(utilizations)
        min_utilization = min(utilizations)
        # print len(utilizations)
        print '{0} {1} {2} {3}'.format(page, median_utilization, min_utilization, max_utilization)

def get_cpu_running_chrome(cpu_running_chrome_filename):
    with open(cpu_running_chrome_filename, 'rb') as input_file:
        return int(input_file.readline())

def populate_offset_dict(custom_offset_filename, offset_dict):
    with open(custom_offset_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            offset_dict[line[0]] = float(line[1]) * 1000.0 # convert to ms

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--start-time-offset', default=None)
    parser.add_argument('--end-time-offset', default=None)
    args = parser.parse_args()
    start_time_offset_dict = dict()
    if args.start_time_offset is not None:
        populate_offset_dict(args.start_time_offset, start_time_offset_dict)
    end_time_offset_dict = dict()
    if args.end_time_offset is not None:
        populate_offset_dict(args.end_time_offset, end_time_offset_dict)
    process_pages(args.root_dir, start_time_offset_dict, end_time_offset_dict)
