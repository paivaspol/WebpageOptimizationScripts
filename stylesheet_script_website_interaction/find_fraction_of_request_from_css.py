from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import simplejson as json


METHOD = 'method'
REQUEST_HEADERS = 'requestHeaders'
PARAMS = 'params'
REFERER = 'referer'
RESPONSE = 'response'
URL = 'url'
DOCUMENT_URL = 'documentURL'

def process_files(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for directory in os.listdir(root_dir):
        # if directory != 'apple.com':
        #    continue
        network_filename = os.path.join(root_dir, directory, 'network_' + directory)
        if not os.path.exists(network_filename):
            continue
        find_requests(network_filename, directory)

def find_requests(network_filename, page):
    found_first_request = False
    result = set()
    total_requests = 0
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                if common_module.escape_page(network_event[PARAMS][DOCUMENT_URL]) \
                    == page:
                    found_first_request = True
            if not found_first_request:
                continue
            if network_event[METHOD] == 'Network.responseReceived':
                referer = None
                if PARAMS in network_event and \
                    REQUEST_HEADERS in network_event[PARAMS][RESPONSE] and \
                    REFERER in network_event[PARAMS][RESPONSE][REQUEST_HEADERS]:
                    referer = network_event[PARAMS][RESPONSE][REQUEST_HEADERS][REFERER]
                if referer is not None:
                    parsed_referer = urlparse(referer)
                    if parsed_referer.path.endswith('.css'):
                        result.add(network_event[PARAMS][RESPONSE][URL])
                total_requests += 1
    print page + ' ' + str(len(result)) + ' ' + str(total_requests)
    return result, total_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_files(args.root_dir)
