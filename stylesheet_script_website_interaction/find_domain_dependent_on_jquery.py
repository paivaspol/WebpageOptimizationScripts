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

def process_pages(root_dir, experiment_result_root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    all_error_urls = set()
    page_to_request_to_url_dict = dict()
    for page in pages:
        result = process_page(root_dir, experiment_result_root_dir, page)
        if result is not None:
            all_error_urls |= result
            request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
            page_to_request_to_url_dict[page] = common_module.parse_request_to_url(request_id_to_url_filename)
    find_js_domains(all_error_urls, page_to_request_to_url_dict)

def find_js_domains(all_error_urls, page_to_request_to_url_dict):
    total = 0
    same_domain = 0
    external_domain = 0
    for error_url in all_error_urls:
        page, request = extract_page_and_request_from_url(error_url)
        if page in page_to_request_to_url_dict:
            request_to_url_dict = page_to_request_to_url_dict[page]
            if request in request_to_url_dict:
                url = request_to_url_dict[request]
                domain = common_module.extract_domain(url)
                if domain == page:
                    same_domain += 1
                else:
                    external_domain += 1
                total += 1
                print page + ' ' + domain + ' ' + url
    print 'same: {0} external: {1} total: {2}'.format(same_domain, external_domain, total)

def extract_page_and_request_from_url(url):
    # http://apple-pi.eecs.umich.edu/grouped_domain_script_execution/meaww.com/19403.9
    first_slash = -1
    second_slash = -1
    for i in range(len(url) - 1, 0, -1):
        if url[i] == '/':
            if second_slash == -1:
                second_slash = i
            elif first_slash == -1:
                first_slash = i
            if first_slash != -1 and second_slash != -1:
                break
    page = url[first_slash + 1: second_slash]
    request = url[second_slash + 1: len(url)]
    return page, request

def process_page(root_dir, experiment_result_root_dir, page):
    all_error_urls = set()
    page_id_to_domain_filename = os.path.join(root_dir, page, 'page_id_to_domain_mapping.txt')
    if not os.path.exists(page_id_to_domain_filename):
        return
    page_to_domain_mapping = common_module.parse_page_id_to_domain_mapping(page_id_to_domain_filename)
    for page_id, domain in page_to_domain_mapping.iteritems():
        page_filename = page_id + '.html'
        page_directory = DIRECTORY.format(page, page_filename)
        path_to_result = os.path.join(experiment_result_root_dir, page_directory)
        console_filename = os.path.join(path_to_result, 'console_' + page_directory)
        if not os.path.exists(console_filename):
            continue
        result = parse_console_file(console_filename)
        if result is not None:
            all_error_urls.add(result)
    return all_error_urls

def parse_console_file(console_filename):
    with open(console_filename, 'rb') as input_file:
        for raw_line in input_file:
            console_event = json.loads(json.loads(raw_line.strip()))
            if console_event[METHOD] == 'Console.messageAdded':
                if console_event[PARAMS]['message']['level'] == 'error':
                    error_txt = console_event[PARAMS]['message']['text']
                    if 'Failed to load resource' in error_txt and \
                        'favicon.ico' in console_event[PARAMS]['message']['url']:
                        continue
                    if 'jQuery' in error_txt:
                        return console_event[PARAMS]['message']['url']
    return None

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('experiment_result_root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir, args.experiment_result_root_dir)
