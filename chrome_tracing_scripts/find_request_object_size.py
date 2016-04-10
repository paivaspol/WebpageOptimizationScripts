from argparse import ArgumentParser

import common_module
import simplejson as json
import os

def get_request_sizes(network_filename, start_end_time):
    request_size = dict()
    request_id_to_url = dict()
    start_time, end_time = start_end_time
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if 'timestamp' not in network_event['params']:
                continue

            ts = common_module.convert_to_ms(network_event['params']['timestamp'])
            if not start_time <= ts <= end_time:
                # If the event doesn't fall in the page load range.
                continue
            
            request_id = network_event['params']['requestId']
            if network_event['method'] == 'Network.requestWillBeSent':
                request_size[request_id] = 0
                request_id_to_url[request_id] = network_event['params']['request']['url']
            elif network_event['method'] == 'Network.dataReceived':
                if request_id in request_size:
                    request_size[request_id] += network_event['params']['encodedDataLength']
            elif network_event['method'] == 'Network.loadingFinished':
                request_id = network_event['params']['requestId']
                if request_id in request_size:
                    cumulative_size = request_size[request_id]
                    request_size[request_id] = (max(network_event['params']['encodedDataLength'], cumulative_size), request_id_to_url[request_id])
    request_size = { k: v for (k, v) in request_size.iteritems() if not isinstance(v, int) }
    return request_size

def get_request_sizes_in_directory(root_dir, write_results):
    request_sizes = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        # print path
        url = common_module.extract_url_from_path(path)
        full_path = os.path.join(path, 'network_' + url)
        page_start_end_time = common_module.parse_page_start_end_time(os.path.join(path, 'start_end_time_' + url))
        page_request_sizes = get_request_sizes(full_path, page_start_end_time[2])
        page_request_size_values = [ size[0] for size in page_request_sizes.values() ]
        request_sizes.extend(page_request_size_values)
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
            output_file.write('{0} {1} {2}\n'.format(key, results[key][0], results[key][1]))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--write-results', default=False, action='store_true')
    args = parser.parse_args()
    sorted_request_sizes = get_request_sizes_in_directory(args.root_dir, args.write_results)
    print_results(sorted_request_sizes)
