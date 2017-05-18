from argparse import ArgumentParser 

import constants
import common_module
import os
import json

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'

def main(root_dir):
    for page in os.listdir(root_dir):
        network_event_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_event_filename):
            continue
        num_requests = find_all_requests(network_event_filename)
        if args.min_requests == -1 or num_requests > args.min_requests:
            print '{0} {1}'.format(page, num_requests)

def find_all_requests(network_filename):
    with open(network_filename, 'rb') as input_file:
        counter = 0
        request_id_set = set()
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except Exception:
                network_event = json.loads(raw_line.strip())

            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                request_id_set.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                if request_id in request_id_set:
                    counter += 1
        return counter

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--min-requests', type=int, default=-1)
    args = parser.parse_args()
    main(args.root_dir)
