from argparse import ArgumentParser
from bs4 import BeautifulSoup
from multiprocessing import Pool, freeze_support

import bs4
import common_module
import os
import re
import itertools
import subprocess
import multiprocessing
import simplejson as json
import time

NUM_PROCESSES = 4
URL = 'url\('
DEVICE_SCALING_FACTOR = 3.5

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    common_module.create_directory_if_not_exists(output_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(parse_html_wrapper,\
                    itertools.izip(pages, \
                    itertools.repeat(root_dir), \
                    itertools.repeat(output_dir)))

def parse_html_wrapper(args):
    return parse_html(*args)

def non_parallelized(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        parse_html(page, root_dir, output_dir)

def parse_html(page, root_dir, output_dir):
    page_output_dir = os.path.join(output_dir, page)
    common_module.create_directory_if_not_exists(page_output_dir)
    descendants = set()
    html_filename = os.path.join(root_dir, page, 'before_page_load.html')
    if not os.path.exists(html_filename):
        return
    page_size = os.path.getsize(html_filename)
    print 'processing: ' + page + ' page_size: ' + str(page_size)

    start_time = time.time()
    with open(html_filename, 'rb') as input_file:
        parsed_html = BeautifulSoup(input_file, 'html.parser')
        # parsed_html = BeautifulSoup(input_file, 'lxml')
        element_count = 0
        element_hit = dict()
        for descendant in parsed_html.descendants:
            element_count += 1
            if type(descendant) is bs4.element.Tag and \
                 'src' in descendant.attrs:
                child = descendant['src']
                if 'srcset' in descendant.attrs:
                    child = extract_child_from_srcset(child, descendant['srcset'])
                if not descendant['src'].startswith('data'):
                    descendants.add(child)
                if 'src_attr' not in element_hit:
                    element_hit['src_attr'] = 0
                element_hit['src_attr'] += 1
            elif type(descendant) is bs4.element.Tag and \
                descendant.name == 'link' and \
                (('type' in descendant.attrs and \
                descendant.attrs['type'] == 'text/css') or \
                ('rel' in descendant.attrs and \
                'stylesheet' in descendant.attrs['rel'])) and \
                'href' in descendant.attrs:
                if not descendant['href'].startswith('data'):
                    descendants.add(descendant['href'])
                if 'external_css' not in element_hit:
                    element_hit['external_css'] = 0
                element_hit['external_css'] += 1
            elif type(descendant) is bs4.element.Tag and \
                'style' in descendant.attrs:
                css_value = descendant.attrs['style']
                descendants |= extract_urls_from_css_value(css_value)
                if 'inline_style' not in element_hit:
                    element_hit['inline_style'] = 0
                element_hit['inline_style'] += 1

            # elif type(descendant) is bs4.element.Tag and \
            #     descendant.name == 'style' and \
            #     'href' not in descendant.attrs:
            #         # Need to parse the CSS and get children from the css.
            #         css_str = descendant.string
            #         try:
            #             descendants |= parse_inline_css(css_str, html_filename, str(os.getpid()))
            #         except Exception as e:
            #             print '[ERROR]: ' + page
    end_time = time.time()
    if args.profile_time:
        output_timing(page_output_dir, end_time - start_time, page_size, element_count)
        output_elements_hit(page_output_dir, end_time - start_time, page_size, element_hit)
        
    output_to_file(page_output_dir, descendants)

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

def output_to_file(output_dir, descendants):
    with open(os.path.join(output_dir, 'html_children.txt'), 'wb') as output_file:
        for descendant in descendants:
            output_file.write(descendant.encode('utf8') + '\n')

def output_timing(output_dir, timing, page_size, element_count):
    with open(os.path.join(output_dir, 'html_parsing_runtime.txt'), 'wb') as output_file:
        output_file.write(str(timing * 1000) + ' ' + str(page_size) + ' ' + str(element_count) + '\n')

def output_elements_hit(output_dir, timing, page_size, elements_hit):
    with open(os.path.join(output_dir, 'elements_stats.txt'), 'wb') as output_file:
        for element in elements_hit:
            output_file.write(str(timing * 1000) + ' ' + element + ' ' + str(elements_hit[element]) + '\n')

def remove_relative_path(path):
    result = path
    result.replace('..', '')
    result.replace('.', '')
    while result.starswith('\/'):
        result = result[1:]
    return result

def extract_child_from_srcset(default_url, srcs):
    splitted_srcs = srcs.split(',')
    max_scaling_factor = 1
    best_url = default_url
    for src in splitted_srcs:
        src = src.strip()
        if ' ' in src:
            url, scaling_factor = src.strip().split()
            if scaling_factor.endswith('x') and \
                float(scaling_factor[:len(scaling_factor) - 1]) >= DEVICE_SCALING_FACTOR:
                best_url = url
    return best_url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--profile-time', default=False, action='store_true')
    args = parser.parse_args()
    freeze_support()
    main(args.root_dir, args.output_dir)
    # non_parallelized(args.root_dir, args.output_dir)
