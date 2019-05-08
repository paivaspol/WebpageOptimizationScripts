from argparse import ArgumentParser
from urlparse import urlparse
from multiprocessing import Pool, freeze_support

import common_module
import os
import subprocess
import itertools

NUM_PROCESSES = 4

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    common_module.create_directory_if_not_exists(output_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(process_page_wrapper,\
                    itertools.izip(pages, \
                    itertools.repeat(root_dir), \
                    itertools.repeat(output_dir)))

def process_page_wrapper(args):
    return process_page(*args)

def process_page(page, root_dir, output_dir):
    common_module.create_directory_if_not_exists(os.path.join(output_dir, page))
    scripts = os.listdir(os.path.join(root_dir, page))
    counter = 0
    for script in scripts:
        script_filename = os.path.join(root_dir, page, script)
        output_filename = os.path.join(output_dir, page, str(counter))
        cmd = 'node js_parser.js {0} {1}'.format(script_filename, output_filename)
        subprocess.call(cmd, shell=True)
        counter += 1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
