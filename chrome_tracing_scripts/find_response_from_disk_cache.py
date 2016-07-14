from argparse import ArgumentParser

import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        total_response, from_cache, not_from_cache = process_network_file(network_filename)
        print '{0} {1} {2} {3}'.format(page, from_cache, not_from_cache, total_response)

def process_network_file(network_filename):
    with open(network_filename, 'rb') as input_file:
        total_response_received = 0
        total_served_from_cache = 0
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.responseReceived':
                total_response_received += 1
                if network_event['params']['response']['fromDiskCache']:
                    total_served_from_cache += 1
    return total_response_received, total_served_from_cache, (total_response_received - total_served_from_cache)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)

