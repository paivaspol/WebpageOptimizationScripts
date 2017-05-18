from argparse import ArgumentParser

import common_module
import json
import os

def get_request_sizes(network_filename, page):
    request_size = dict()
    request_id_to_url = dict()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except:
                network_event = json.loads(raw_line.strip())
            if not found_first_request:
                if network_event['method'] == 'Network.requestWillBeSent' and \
                    common_module.escape_page(network_event['params']['request']['url']) == page:
                    found_first_request = True
                else:
                    continue
            
            request_id = network_event['params']['requestId']
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                if not url.startswith('data'):
                    request_size[request_id] = 0
                    request_id_to_url[request_id] = url
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

def get_request_sizes_in_directory(root_dir, write_results, page_list):
    request_sizes = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        print url
        full_path = os.path.join(path, 'network_' + url)
        if not os.path.exists(full_path):
            continue
        page_request_sizes = get_request_sizes(full_path, url)
        page_request_size_values = [ size[0] for size in page_request_sizes.values() ]
        request_sizes.extend(page_request_size_values)
        if write_results:
            full_path = os.path.join(path, 'request_sizes.txt')
            output_to_file(page_request_sizes, full_path)
        elif args.aggregate_dir is not None:
            if not os.path.exists(args.aggregate_dir):
                os.mkdir(args.aggregate_dir)
            output_url = url
            if page_list is not None and url in page_list:
                output_url = page_list[url]
            full_path = os.path.join(args.aggregate_dir, output_url)
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

def get_page_list(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { common_module.escape_page(key): common_module.escape_page(value) for key, value in temp }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--write-results', default=False, action='store_true')
    parser.add_argument('--aggregate-dir', default=None)
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    page_list = None
    if args.page_list is not None:
        page_list = get_page_list(args.page_list)
    sorted_request_sizes = get_request_sizes_in_directory(args.root_dir, args.write_results, page_list)
    print_results(sorted_request_sizes)
