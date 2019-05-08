from argparse import ArgumentParser
from bs4 import BeautifulSoup
from multiprocessing import Pool, freeze_support

import common_module
import itertools
import os

NUM_PROCESSES = 4

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)

    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(process_page_wrapper, itertools.izip(itertools.repeat(root_dir), \
                                              pages))
    for page in pages:
        process_page(root_dir, page)

def process_page_wrapper(args):
    return process_page(*args)

def process_page(root_dir, page):
    html_before_page_load = os.path.join(root_dir, page, 'before_page_load.html')
    html_after_page_load = os.path.join(root_dir, page, 'after_page_load.html')
    if os.path.exists(html_before_page_load) and os.path.exists(html_after_page_load):
        original = find_script_tags(html_before_page_load)
        page_load = find_script_tags(html_after_page_load)
        print '{0} {1} {2}'.format(page, original, page_load)

def find_script_tags(html_filename):
    with open(html_filename, 'rb') as input_file:
        parsed_html = BeautifulSoup(input_file, 'html.parser')
        all_scripts = parsed_html.find_all('script')
        return len(all_scripts)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    freeze_support()
    process_pages(args.root_dir)
