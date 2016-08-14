from argparse import ArgumentParser

import common_module
import numpy
import os
import random
import subprocess

MEDIAN = 'median'
MIN = 'min'
MAX = 'max'
RANDOM = 'random'
HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'

def get_page_to_chosen_run(root_dir, num_iterations, run_type, pages):
    page_to_chosen_run_index_dict = dict()
    for page in pages:
        page = common_module.escape_page(page)
        # print 'Processing: ' + page
        load_times = []

        for i in range(0, num_iterations):
            run_path = os.path.join(os.path.join(root_dir, str(i)), page)
            start_end_time_filename = os.path.join(run_path, 'start_end_time_{0}'.format(page))
            if not os.path.exists(start_end_time_filename):
                continue
            this_run_page_load_time = get_page_load_time(start_end_time_filename)
            load_times.append(this_run_page_load_time)

        # Choose the load time.
        # print 'number of loads: ' + str(len(load_times))
        if len(load_times) > 0:
            if run_type == MEDIAN:
                chosen_load_time = numpy.median(load_times)
            elif run_type == MIN:
                chosen_load_time = min(load_times)
            elif run_type == MAX:
                chosen_load_time = max(load_times)
            elif run_type == RANDOM:
                chosen_load_time = random.sample(load_times, 1)[0]
            page_to_chosen_run_index_dict[page] = find_index_for_load_time(chosen_load_time, load_times)
    return page_to_chosen_run_index_dict

def find_index_for_load_time(target_page_load_time, load_times):
    for i in range(0, len(load_times)):
        load_time = load_times[i]
        if target_page_load_time == load_time:
            return i
    return -1

def get_page_load_time(start_end_time_filename):
    '''
    Returns the page load time from the file.
    '''
    with open(start_end_time_filename, 'rb') as start_end_time_file:
        line = start_end_time_file.readline().strip().split()
        return int(line[2]) - int(line[1])

def get_pages(pages_file):
    '''
    Returns a list of page names.
    '''
    result = []
    with open(pages_file, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            page = common_module.escape_page(line[len(line) - 1])
            result.append(page)
    return result

def copy_chosen_runs(chosen_runs, root_dir, output_dir, num_iterations):
    '''
    Copies the chosen runs to the output directory.
    '''
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    counter = 0
    for page, run_index in chosen_runs.iteritems():
        if 0 <= run_index < num_iterations:
            run_path = os.path.join(os.path.join(root_dir, str(run_index)), page)
            copy_command = 'cp -r {0} {1}'.format(run_path, output_dir)
            subprocess.call(copy_command, shell=True)
            counter += 1
            print '{0} {1}'.format(page, run_index)
    print 'Copied {0} sites from {1} sites'.format(counter, len(chosen_runs))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_file')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('run_type')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    if args.run_type == MIN or args.run_type == MEDIAN or args.run_type == MAX or args.run_type == RANDOM:
        pages = get_pages(args.pages_file)
        chosen_runs = get_page_to_chosen_run(args.root_dir, args.num_iterations, args.run_type, pages)
        copy_chosen_runs(chosen_runs, args.root_dir, args.output_dir, args.num_iterations)
