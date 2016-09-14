from argparse import ArgumentParser
from multiprocessing import Pool, freeze_support

import os
import itertools
import subprocess

NUM_PROCESSES = 4

def main(root_dir, page_to_timestamps, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    indices = range(0, len(page_to_timestamps))

    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(modify_page_wrapper, itertools.izip( \
                                            page_to_timestamps.iteritems(), \
                                            itertools.repeat(root_dir), \
                                            itertools.repeat(output_dir), \
                                            indices))

def modify_page_wrapper(args):
    return modify_page(*args)

def modify_page(page_timestamp_tuple, root_dir, output_dir, index):
    page, timestamp = page_timestamp_tuple
    print 'Generating: ' + page
    page_directory = os.path.join(root_dir, timestamp, page)
    page_output_directory = os.path.join(output_dir, page)

    if not os.path.exists(page_directory):
        return

    # This is already the source directory.
    # Use this directory and use the modify_page.py
    # To include the scheduler.
    generate_command = 'python modify_page.py {0} {1} {2}'
    subprocess.call(generate_command.format(page_directory, page_output_directory, index), shell=True)

def get_times(time_filename):
    with open(time_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: value for key, value in temp }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_to_timestamp')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    page_to_timestamps = get_times(args.page_to_timestamp)
    main(args.root_dir, page_to_timestamps, args.output_dir)
