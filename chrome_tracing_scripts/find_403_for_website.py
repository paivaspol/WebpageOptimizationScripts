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

def find_failed_pages(root_dir, pages):
    for page in pages:
        removed_prefix = page[len(HTTP_PREFIX):]
        if removed_prefix.startswith(WWW_PREFIX):
            removed_prefix = removed_prefix[len(WWW_PREFIX):]
        removed_prefix = removed_prefix.replace('/', '_')
        directory_path = os.path.join(root_dir, removed_prefix)
        if os.path.exists(directory_path):
            network_filename = os.path.join(directory_path, 'network_' + removed_prefix)
            network_events = parse_network_events(network_filename)
            #print page
            if find_if_load_failed(network_events, page):
                pass
                print page

def find_if_load_failed(network_events, page):
    page_loader_id = None
    for network_event in network_events:
        if network_event[METHOD] == 'Network.requestWillBeSent':
            document_url = network_event[PARAMS][DOCUMENT_URL]
            if document_url.startswith(page):
                page_loader_id = network_event[PARAMS][LOADER_ID]
        elif network_event[METHOD] == 'Network.responseReceived':
            this_response_loader_id = network_event[PARAMS][LOADER_ID]
            if this_response_loader_id == page_loader_id:
                status = network_event[PARAMS]['response']['status']
                if int(status) == 403:
                    # Found the response to the page.
                    return True
                else:
                    return False
    return False

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
    find_failed_pages(args.root_dir, pages)
