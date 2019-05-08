from argparse import ArgumentParser
from urlparse import urlparse

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

def main(root_dir):
    pages = os.listdir(root_dir)
    page_to_missing_resources_mapping = dict()
    domains_to_make_requests = set()
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        results = find_name_resolution_errors(page, network_filename)
        if len(results) > 0:
            print page

def find_name_resolution_errors(page, network_filename):
    # print dependencies
    results = []
    with open(network_filename, 'rb') as input_file:
        times_from_first_request = dict()
        found_first_request = False
        first_request_timestamp = -1
        request_id_to_url_map = dict()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]
                request_id_to_url_map[request_id] = url

            elif network_event[METHOD] == 'Network.loadingFailed':
                request_id = network_event[PARAMS][REQUEST_ID]
                if 'errorText' in network_event[PARAMS] and \
                    network_event[PARAMS]['errorText'] == 'net::ERR_NAME_NOT_RESOLVED':
                    results.append(request_id_to_url_map[request_id])
    return results

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
