from argparse import ArgumentParser 
from collections import defaultdict

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

def main(network_event_filename, dependency_file):
    dependencies = common_module.get_dependencies(dependency_file)
    find_all_requests(network_event_filename, dependencies)

def find_all_requests(network_filename, dependencies):
    # print dependencies
    request_to_url = dict()
    request_timestamp = dict()
    request_to_initiator = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]
                if url in dependencies:
                    request_timestamp[request_id] = network_event[PARAMS][TIMESTAMP]
                    request_to_url[request_id] = url
                    dependencies.remove(url)
                    if args.print_initiator:
                        request_to_initiator[request_id] = network_event[PARAMS]['initiator']
            elif network_event[METHOD] == 'Network.responseReceived':
                if request_id in request_timestamp:
                    timestamp = network_event[PARAMS][TIMESTAMP]
                    time_to_response = timestamp - request_timestamp[request_id]
                    print request_to_url[request_id] + ' time_to_response: ' + str(time_to_response)
                    if args.print_initiator:
                        print request_to_initiator[request_id]
                    if len(dependencies) == 0:
                        break

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_event_filename')
    parser.add_argument('dependency_file')
    parser.add_argument('--print-initiator', default=False, action='store_true')
    args = parser.parse_args()
    main(args.network_event_filename, args.dependency_file)
