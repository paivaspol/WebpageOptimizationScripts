from argparse import ArgumentParser

import common_module
import constants
import os
import math
import simplejson as json

def main(root_dir, percents):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        requests = get_requests_set(network_filename, page)
        thresholds = compute_thresholds(len(requests), percents)
        fraction_load_times = find_fraction_load_time(network_filename, thresholds, page, requests)
        output_str = page
        for load_time in fraction_load_times:
            output_str += ' ' + str(load_time)
        print output_str

def find_fraction_load_time(network_filename, thresholds, page, request_set):
    counter = 0
    result = [ -1 for i in range(0, len(thresholds)) ]
    found_first_request = False
    first_request_timestamp = -1
    max_time = -1
    with open(network_filename, 'rb') as input_file:
        for line in input_file:
            try:
                network_event = json.loads(json.loads(line.strip()))
            except Exception:
                network_event = json.loads(line.strip())

            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if not found_first_request:
                    if common_module.escape_page(url) == page:
                        found_first_request = True
                        first_request_timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                    else:
                        continue
            elif found_first_request and network_event[constants.METHOD] == 'Network.loadingFinished':
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in request_set:
                    counter += 1
                    timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                    for i in range(0, len(thresholds)):
                        if counter > thresholds[i] and result[i] == -1:
                            result[i] = timestamp - first_request_timestamp
                    max_time = max(max_time, timestamp - first_request_timestamp)
    for i in range(0, len(thresholds)):
        if result[i] == -1:
            result[i] = max_time
    return result

def compute_thresholds(num_requests, percents):
    return [ int(math.ceil(num_requests * (1.0 * x / 100))) for x in percents ]

def get_requests_set(network_filename, page):
    requests = set()
    found_first_request = False
    found_request_id = set()
    urls_found = set()
    with open(network_filename, 'rb') as input_file:
        for line in input_file:
            try:
                network_event = json.loads(json.loads(line.strip()))
            except Exception:
                network_event = json.loads(line.strip())

            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if not found_first_request:
                    if common_module.escape_page(url) == page:
                        found_first_request = True
                    else:
                        continue
                if url not in urls_found:
                    urls_found.add(url)
                    found_request_id.add(request_id)
            elif found_first_request and network_event[constants.METHOD] == 'Network.loadingFinished':
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in found_request_id:
                    requests.add(request_id)
    return requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('percents', nargs='+', type=int)
    args = parser.parse_args()
    main(args.root_dir, args.percents)
