from argparse import ArgumentParser
from urlparse import urlparse
from multiprocessing import Pool, freeze_support

import common_module
import itertools
import os
import simplejson as json

PARAMS = 'params'
REQUEST = 'request'
RESPONSE = 'response'
INITIATOR = 'initiator'
TYPE = 'type'
REQUEST_HEADERS = 'requestHeaders'
REFERER = 'Referer'
URL = 'url'
HEADERS = 'headers'
REQUEST_ID = 'requestId'
STACK_TRACE = 'stackTrace'

NUM_PROCESSES = 4

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(process_page_wrapper,\
                    itertools.izip(pages, \
                    itertools.repeat(root_dir), \
                    itertools.repeat(output_dir)))

def process_page_wrapper(args):
    try:
        return process_page(*args)
    except Exception as e:
        pass

def testing(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    page = 'newegg.com'
    process_page(page, root_dir, output_dir)

def process_page(page, root_dir, output_dir):
    common_module.create_directory_if_not_exists(os.path.join(output_dir, page))
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not os.path.exists(network_filename):
        return
    html_children = set()
    css_children = set()
    script_children = set()
    inline_script_children = set()
    documentURL = None
    first_request = None
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            # find the proper first request.
            if first_request is None and REQUEST_ID in network_event[PARAMS] \
                and REQUEST in network_event[PARAMS] \
                and page in network_event[PARAMS][REQUEST][URL]:
                first_request = network_event[PARAMS][REQUEST_ID]

            if network_event['method'] == 'Network.requestWillBeSent':
                if first_request == network_event[PARAMS][REQUEST_ID]:
                    documentURL = network_event[PARAMS]['documentURL']
                request = network_event
                if INITIATOR in request[PARAMS] and \
                    request[PARAMS][INITIATOR][TYPE] == 'parser':
                    # Two Cases: HTML or CSS. Check Referer
                    if REFERER in request[PARAMS][REQUEST][HEADERS]:
                        referer = request[PARAMS][REQUEST][HEADERS][REFERER]
                        parsed_referer = urlparse(referer)
                        if parsed_referer.path.endswith('.css'):
                            css_children.add(request[PARAMS][REQUEST][URL])
                        else:
                            if documentURL in network_event[PARAMS]['documentURL']:
                                html_children.add(request[PARAMS][REQUEST][URL])
                elif INITIATOR in request[PARAMS] and \
                    request[PARAMS][INITIATOR][TYPE] == 'script':
                    if STACK_TRACE in request[PARAMS][INITIATOR] and \
                        documentURL == request[PARAMS][INITIATOR][STACK_TRACE][0]['url']:
                        inline_script_children.add(request[PARAMS][REQUEST][URL])
                    else:
                        script_children.add(request[PARAMS][REQUEST][URL])

    output_to_file(output_dir, page, 'html_children.txt', html_children)
    output_to_file(output_dir, page, 'css_children.txt', css_children)
    output_to_file(output_dir, page, 'script_children.txt', script_children)
    output_to_file(output_dir, page, 'inline_script_children.txt', inline_script_children)
    output_to_file(output_dir, page, 'all_children.txt', html_children | css_children | script_children | inline_script_children)

def output_to_file(output_dir, page, output_filename, children_set):
    common_module.create_directory_if_not_exists(os.path.join(output_dir, page, 'actual'))
    output_filename = os.path.join(output_dir, page, 'actual', output_filename)
    with open(output_filename, 'wb') as output_file:
        for child in children_set:
            output_file.write(child + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    freeze_support()
    main(args.root_dir, args.output_dir)
    # testing(args.root_dir, args.output_dir)
