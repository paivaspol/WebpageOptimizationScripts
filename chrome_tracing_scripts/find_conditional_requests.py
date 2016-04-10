from argparse import ArgumentParser

import common_module
import os
import simplejson as json

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
PARAMS = 'params'
METHOD = 'method'
DOCUMENT_URL = 'documentURL'
LOADER_ID = 'requestId'

def process_pages(root_dir, pages):
    result = []
    for page in pages:
        url = common_module.escape_page(page)
        print 'Processing: ' + url + ' for page: ' + page
        directory_path = os.path.join(root_dir, url)
        if os.path.exists(directory_path):
            network_filename = os.path.join(directory_path, 'network_' + url)
            if not os.path.exists(network_filename):
                continue
            network_events = parse_network_events(network_filename)
            find_conditional_get(network_events, page)

def find_conditional_get(network_events, page):
    total_requests = 0
    found_root = False
    for network_event in network_events:
        if not found_root and network_event[METHOD] == 'Network.requestWillBeSent':
            request_url = network_event[PARAMS]['request']['url']
            # print 'request url: {0} page: {1}'.format(request_url, page)
            found_root = request_url == page

        if not found_root:
            continue

        if network_event[METHOD] == 'Network.requestWillBeSent':
            request_id = network_event[PARAMS]['requestId']
            headers = network_event[PARAMS]['request']['headers']
            print headers
            total_requests += 1
    return total_requests

def parse_network_events(network_events_filename):
    network_events = []
    with open(network_events_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            network_events.append(json.loads(json.loads(line)))
    return network_events

def parse_pages(pages_filename):
    '''
    Parses the pages file.
    '''
    pages = []
    with open(pages_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            pages.append(line[len(line) - 1])
    return pages

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    pages = parse_pages(args.pages_filename)
    process_pages(args.root_dir, pages)
