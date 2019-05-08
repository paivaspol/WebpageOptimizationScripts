from argparse import ArgumentParser
from bs4 import BeautifulSoup
from multiprocessing import Pool, freeze_support

import common_module
import itertools
import os
import re
import simplejson as json

CSS_TYPE = 'type'
CSS_DOWNLOAD = 'download'
CSS_URL = 'url'
CSS_RULE = 'rule'
CSS_FONTFACE = 'font-face'

URL = 'url\('

NUM_PROCESSES = 4

def main(root_dir, css_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    common_module.create_directory_if_not_exists(output_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(find_css_children_wrapper,\
                    itertools.izip(pages, \
                    itertools.repeat(root_dir), \
                    itertools.repeat(css_dir), \
                    itertools.repeat(output_dir)))

def find_css_children_wrapper(args):
    return find_css_children(*args)

def find_css_children(page, root_dir, css_dir, output_dir):
    print 'processing: ' + page
    page_css_dir = os.path.join(css_dir, page)
    if not os.path.exists(page_css_dir):
        return

    page_output_directory = os.path.join(output_dir, page)
    common_module.create_directory_if_not_exists(page_output_directory)
    original_html_filename = os.path.join(root_dir, page, 'before_page_load.html')
    if not os.path.exists(original_html_filename):
        return

    parsed_html = BeautifulSoup(open(original_html_filename), 'html.parser')
    css_files = os.listdir(page_css_dir)
    css_children = set()
    for css_file in css_files:
        with open(os.path.join(page_css_dir, css_file), 'rb') as css_file_obj:
            css_rule_declarations = json.load(css_file_obj)['results']
            for css_rule_declaration in css_rule_declarations:
                if CSS_TYPE not in css_rule_declaration:
                    continue

                if css_rule_declaration[CSS_TYPE] == CSS_FONTFACE:
                    url = extract_urls_from_fontface_urls(css_rule_declaration[CSS_URL])
                    if url is not None:
                        css_children.add(url)
                elif css_rule_declaration[CSS_TYPE] == CSS_RULE:
                    # Also handle selector.
                    for selector in css_rule_declaration['selectors']:
                        try:
                            result_from_selector = parsed_html.select(selector)
                            if len(result_from_selector) > 0:
                                css_children |= extract_urls_from_css_value(css_rule_declaration[CSS_URL])
                        except (ValueError, NotImplementedError) as e:
                            pass
    output_to_file(css_children, output_dir, page)

def output_to_file(css_children, output_dir, page):
    if args.inline_css:
        with open(os.path.join(output_dir, page, 'html_children.txt'), 'ab') as output_file:
            for css_child in css_children:
                output_file.write(css_child.encode('utf8') + '\n')
    else:
        with open(os.path.join(output_dir, page, 'css_children.txt'), 'wb') as output_file:
            for css_child in css_children:
                output_file.write(css_child.encode('utf8') + '\n')

def extract_urls_from_css_value(css_value):
    urls = set()
    start_locations = [ m.start() for m in re.finditer(URL, css_value) ]
    for start_location in start_locations:
        counter = start_location
        cur_char = css_value[start_location]
        cur_url = ''
        while cur_char != ')':
            cur_url += cur_char
            counter += 1
            cur_char = css_value[counter]
        cur_url = remove_url_prefix_and_suffix(cur_url)
        if not cur_url.startswith('data'):
            urls.add(cur_url)
    return urls

def extract_urls_from_fontface_urls(css_value):
    urls = set()
    start_locations = [ m.start() for m in re.finditer(URL, css_value) ]
    for start_location in start_locations:
        counter = start_location
        cur_char = css_value[start_location]
        cur_url = ''
        while cur_char != ')':
            cur_url += cur_char
            counter += 1
            cur_char = css_value[counter]
        cur_url = remove_url_prefix_and_suffix(cur_url)
        if not cur_url.startswith('data') and 'woff' in os.path.splitext(cur_url)[1]:
            return cur_url
    return None

def remove_url_prefix_and_suffix(url):
    if url.startswith('url('):
        url = url[len('url('):]
    if url.endswith(')'):
        url = url[:len(url) - 1]
    if url.startswith('"') or url.startswith('\''):
        url = url[1:]
    if url.endswith('"') or url.endswith('\''):
        url = url[:len(url) - 1]
    return url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('css_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--inline-css', default=False, action='store_true')
    args = parser.parse_args()
    freeze_support()
    main(args.root_dir, args.css_dir, args.output_dir)
