from argparse import ArgumentParser

import common_module
import simplejson as json
import os

def get_request_sizes(network_filename):
    request_size = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.requestWillBeSent':
                request_size[network_event['params']['requestId']] = 0
            elif network_event['method'] == 'Network.dataReceived':
                request_size[network_event['params']['requestId']] += network_event['params']['encodedDataLength']
            elif network_event['method'] == 'Network.loadingFinished':
                cumulative_size = request_size[network_event['params']['requestId']]
                request_size[network_event['params']['requestId']] = max(network_event['params']['encodedDataLength'], cumulative_size)
    return request_size

def get_request_sizes_in_directory(root_dir, write_results):
    request_sizes = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        # print path
        url = common_module.extract_url_from_path(path)
        full_path = os.path.join(path, 'network_' + url)
        page_request_sizes = get_request_sizes(full_path)
        request_sizes.extend(page_request_sizes.values())
        if write_results:
            full_path = os.path.join(path, 'request_sizes.txt')
            output_to_file(page_request_sizes, full_path)
    request_sizes.sort()
    return request_sizes

def print_results(results):
    for result in results:
        print result

def output_to_file(results, output_filename):
    with open(output_filename, 'wb') as output_file:
        for key in results:
            output_file.write('{0} {1}\n'.format(key, results[key]))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--write-results', default=False, action='store_true')
    args = parser.parse_args()
    sorted_request_sizes = get_request_sizes_in_directory(args.root_dir, args.write_results)
    print_results(sorted_request_sizes)
