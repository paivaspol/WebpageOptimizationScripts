from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        difference, response_received_walltime = find_difference(network_filename, page)
        print '{0} {1} {2}'.format(page, difference, response_received_walltime)

def find_difference(network_filename, page):
    with open(network_filename, 'rb') as input_file:
        request_id = None
        initial_timestamp = -1
        initial_walltime = -1
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                if common_module.escape_page(url) == page:
                    request_id = network_event['params']['requestId']
                    initial_timestamp = network_event['params']['timestamp']
                    initial_walltime = network_event['params']['wallTime']
            elif network_event['method'] == 'Network.responseReceived':
                if network_event['params']['requestId'] == request_id:
                    difference = network_event['params']['timestamp'] - initial_timestamp
                    return difference, (initial_walltime + difference)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
