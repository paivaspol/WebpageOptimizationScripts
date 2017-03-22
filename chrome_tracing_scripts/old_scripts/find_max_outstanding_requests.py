from argparse import ArgumentParser

import common_module
import simplejson as json
import os

def find_number_of_requests(root_dir):
    result = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        network_filename = os.path.join(path, 'network_' + url)
        max_num_outstanding_requests = 0
        unique_requests = set()
        with open(network_filename, 'rb') as input_file:
            for raw_line in input_file:
                network_event = json.loads(json.loads(raw_line.strip()))
                if network_event['method'] == 'Network.requestWillBeSent':
                    unique_requests.add(network_event['params']['requestId'])
                elif network_event['method'] == 'Network.loadingFinished':
                    unique_requests.remove(network_event['params']['requestId'])
                max_num_outstanding_requests = max(max_num_outstanding_requests, len(unique_requests))
        result.append((url, max_num_outstanding_requests))
    
    sorted_number_of_objects = sorted([ (url, num_objects) for url, num_objects in result if num_objects >= 41 ], key= lambda x: x[1])
    for num_obj in sorted_number_of_objects:
        print '{0} {1}'.format(num_obj[0], num_obj[1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    find_number_of_requests(args.root_dir)

