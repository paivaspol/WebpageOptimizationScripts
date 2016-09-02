from argparse import ArgumentParser 

import constants
import common_module
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'

def main(root_dir, page_list, min_requests):
    pages = get_pages(page_list)
    for page in pages:
        escaped_page = common_module.escape_page(page)
        network_event_filename = os.path.join(root_dir, escaped_page, 'network_' + escaped_page)
        if not os.path.exists(network_event_filename):
            continue
        num_requests = find_all_requests(network_event_filename)
        if num_requests > min_requests:
            print page

def find_all_requests(network_filename):
    with open(network_filename, 'rb') as input_file:
        counter = 0
        request_id_set = set()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                request_id_set.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                if request_id in request_id_set:
                    counter += 1
        return counter

def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        return [ line.strip() for line in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('min_requests', type=int)
    args = parser.parse_args()
    main(args.root_dir, args.page_list, args.min_requests)
