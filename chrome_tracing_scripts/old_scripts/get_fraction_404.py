from argparse import ArgumentParser

import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
RESPONSE = 'response'
STATUS = 'status'

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        failed_requests, request_set = get_fraction_404(network_filename)
        if len(request_set) > 0:
            fraction_of_404 = 1.0 * len(failed_requests) / len(request_set)
            print '{0} {1} {2} {3}'.format(page, len(failed_requests), len(request_set), fraction_of_404)
            if args.print_missed_resources:
                print [ x for _, x in failed_requests ]

def get_fraction_404(network_filename):
    with open(network_filename, 'rb') as input_file:
        request_set = set()
        failed_requests = set()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                request_id = network_event[PARAMS][REQUEST_ID]
                request_set.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                request_id = network_event[PARAMS][REQUEST_ID]
                if request_id in request_set:
                    url = network_event[PARAMS][RESPONSE]['url']
                    status_code = int(network_event[PARAMS][RESPONSE][STATUS])
                    if status_code == 404:
                        failed_requests.add((request_id, url))
        return failed_requests, request_set

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--print-missed-resources', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir)
