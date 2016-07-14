from argparse import ArgumentParser
from bs4 import BeautifulSoup, NavigableString

import common_module
import os

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        process_page(root_dir, page)

def process_page(root_dir, page):
    before_page_load = os.path.join(root_dir, page, 'before_page_load.html')
    after_page_load = os.path.join(root_dir, page, 'after_page_load.html')
    if os.path.exists(before_page_load) and os.path.exists(after_page_load):
        before_page_load_script_count = get_num_script_tags(before_page_load)
        after_page_load_script_count = get_num_script_tags(after_page_load)
        print '{0} {1} {2}'.format(page, before_page_load_script_count, after_page_load_script_count)

def get_num_script_tags(html_filename):
    soup = BeautifulSoup(open(html_filename), 'html.parser')
    num_script_tags = len(soup.find_all('script'))
    return num_script_tags

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
