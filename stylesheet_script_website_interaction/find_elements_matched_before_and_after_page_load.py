from argparse import ArgumentParser
from bs4 import BeautifulSoup
from multiprocessing import Pool, freeze_support
from urlparse import urlparse

import common_module
import itertools
import os

NUM_PROCESSES = 4

def find_matched_difference_in_directory(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    pages = os.listdir(root_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(find_matched_difference_wrapper, itertools.izip(itertools.repeat(root_dir), \
                                                  pages, itertools.repeat(output_dir)))

def find_matched_difference(root_dir, directory, output_dir):
    print 'Processing: ' + directory
    common_module.create_directory_if_not_exists(os.path.join(output_dir, directory))
    html_before_page_load = os.path.join(root_dir, directory, 'before_page_load.html')
    html_after_page_load = os.path.join(root_dir, directory, 'after_page_load.html')
    request_id_to_url_mapping_filename = os.path.join(root_dir, directory, 'request_id_to_url.txt')
    if not (os.path.exists(html_before_page_load) and \
            os.path.exists(html_after_page_load) and \
            os.path.exists(request_id_to_url_mapping_filename)):
        return;
    # before_page_load_html_str = get_html_string(html_before_page_load)
    before_page_load_html = BeautifulSoup(open(html_before_page_load), 'html.parser')
    # after_page_load_html_str = get_html_string(html_after_page_load)
    after_page_load_html = BeautifulSoup(open(html_after_page_load), 'html.parser')
    css_files = get_css_files(request_id_to_url_mapping_filename)
    summary_dict = dict()
    for css_file in css_files:
        css_full_path = os.path.join(root_dir, directory, css_file)
        if not os.path.exists(css_full_path):
            continue
        selectors = parse_css(css_full_path)
        # print 'css_file: ' + css_file + ' selector len: ' + str(len(selectors))
        before_page_load_matched = find_elements_matched_by_selectors(before_page_load_html, \
                                                                      selectors)
        after_page_load_matched = find_elements_matched_by_selectors(after_page_load_html, \
                                                                     selectors)
        summary_dict[css_file] = (sum(before_page_load_matched.values()), sum(after_page_load_matched.values()))
        write_result_detailed(output_dir, directory, css_file, before_page_load_matched, after_page_load_matched)
    write_result_summary(output_dir, directory, summary_dict)

def find_matched_difference_wrapper(args):
    return find_matched_difference(*args)

def write_result_detailed(output_dir, directory, css_file, before_page_load_matched, after_page_load_matched):
    output_filename = os.path.join(output_dir, directory, css_file)
    selector_map_filename = os.path.join(output_dir, directory, 'selector_map.txt')
    with open(output_filename, 'wb') as output_file, open(selector_map_filename, 'wb') as selector_map_file:
        counter = 0
        for selector in before_page_load_matched:
            matched_after_page_load = 0
            if selector in after_page_load_matched:
                matched_after_page_load = after_page_load_matched[selector]
                del after_page_load_matched[selector]
            output_file.write('{0} {1} {2}\n'.format(counter, before_page_load_matched[selector], matched_after_page_load))
            selector_map_file.write('{0} {1}\n'.format(counter, selector))
            counter += 1

        # At this point, there isn't any selector in the before page load that we haven't covered.
        for selector in after_page_load_matched:
            output_file.write('{0} {1} {2}\n'.format(counter, 0, matched_after_page_load))
            selector_map_file.write('{0} {1}\n'.format(counter, selector))
            counter += 1

def write_result_summary(output_dir, directory, matched_summary):
    output_filename = os.path.join(output_dir, directory, 'summary.txt')
    with open(output_filename, 'wb') as output_file:
        for css_file in matched_summary:
            output_file.write('{0} {1} {2}\n'.format(css_file, matched_summary[css_file][0], matched_summary[css_file][1]))

def parse_css(css_filename):
    selectors = set()
    with open(css_filename, 'rb') as input_file:
        raw_line = input_file.readline()
        found_selector = False
        selector = ''
        while raw_line != '':
            line = raw_line.rstrip()
            if line.startswith('.') or line[:1].isalpha() or line.startswith('#'):
                found_selector = True   # We have found a selector start it here.
                for c in line:
                    if c != '{':
                        selector += c
                    else:
                        # We have complete the discovering a selector
                        found_selector = False
                        if not selector.startswith('only screen'):
                            # print selector
                            selectors.add(selector)
                        selector = ''
                        break
            raw_line = input_file.readline()
    return selectors

def find_elements_matched_by_selectors(html, selectors):
    result_dict = dict()
    for selector in selectors:
        try:
            result = html.select(selector)
            result_dict[selector] = len(result)
        except Exception as e:
            pass
    return result_dict

def get_html_string(html_filename):
    html_str = ''
    with open(html_filename, 'rb') as input_file:
        for raw_line in input_file:
            html_str += raw_line
    return html_str

def get_css_files(request_id_to_url_mapping_filename):
    css_files = []
    with open(request_id_to_url_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parsed_url = urlparse(line[1])
            if parsed_url.path.endswith('.css'):
                css_files.append(line[0] + '.beautified')
    return css_files

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    freeze_support()
    find_matched_difference_in_directory(args.root_dir, args.output_dir)
