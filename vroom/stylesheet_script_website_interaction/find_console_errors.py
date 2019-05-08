from argparse import ArgumentParser

import common_module
import os
import simplejson as json

DIRECTORY = 'apple-pi.eecs.umich.edu_grouped_domain_script_execution_{0}_{1}'
PARAMS = 'params'
METHOD = 'method'
REQUEST = 'request'

# Javascript Constants
INITIATOR = 'initiator'
TYPE = 'type'
SCRIPT = 'script'
STACK_TRACE = 'stackTrace'
URL = 'url'

def process_directories(root_dir, experiment_result_root_dir):
    pages = os.listdir(root_dir)
    overall_histogram = dict()
    for page in pages:
        page_histogram = process_page(root_dir, experiment_result_root_dir, page)
        populate_histogram(overall_histogram, page_histogram)
    # print_histogram(overall_histogram)

def print_histogram(histogram, prefix=''):
    sorted_histogram = sorted(histogram.items(), key=lambda x: x[1], reverse=True)
    for key, value in sorted_histogram:
        key_str = key.encode('ascii', 'ignore')
        if len(key_str) < 100:
            print '{0}{1} {2}'.format(prefix, key_str, value)

def process_page(root_dir, experiment_result_root_dir, page):
    page_to_domain_mapping_filename = os.path.join(root_dir, page, 'page_id_to_domain_mapping.txt')
    page_histogram = dict()
    if not os.path.exists(page_to_domain_mapping_filename):
        return page_histogram
    page_to_domain_mapping = common_module.parse_page_id_to_domain_mapping(page_to_domain_mapping_filename)
    for page_id, domain in page_to_domain_mapping.iteritems():
        page_filename = page_id + '.html'
        page_directory = DIRECTORY.format(page, page_filename)
        path_to_result = os.path.join(experiment_result_root_dir, page_directory)
        console_filename = os.path.join(path_to_result, 'console_' + page_directory)
        if not os.path.exists(console_filename):
            continue
        histogram = parse_console_file(console_filename)
        populate_histogram(page_histogram, histogram)
    print page
    print_histogram(page_histogram, prefix='\t')
    return page_histogram

def populate_histogram(base_histogram, new_histogram):
    for key in new_histogram:
        if key not in base_histogram:
            base_histogram[key] = 0
        base_histogram[key] += new_histogram[key]

def parse_console_file(console_filename):
    histogram = dict()
    with open(console_filename, 'rb') as input_file:
        for raw_line in input_file:
            console_event = json.loads(json.loads(raw_line.strip()))
            if console_event[METHOD] == 'Console.messagesCleared':
                # Done with console events
                break
            elif console_event[METHOD] == 'Console.messageAdded':
                if console_event[PARAMS]['message']['level'] == 'error':
                    error_txt = console_event[PARAMS]['message']['text']
                    if 'Failed to load resource' in error_txt and \
                        'favicon.ico' in console_event[PARAMS]['message']['url']:
                        continue
                    if error_txt not in histogram:
                        histogram[error_txt] = 0
                    histogram[error_txt] += 1
    return histogram

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('experiment_result_root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_directories(args.root_dir, args.experiment_result_root_dir)
