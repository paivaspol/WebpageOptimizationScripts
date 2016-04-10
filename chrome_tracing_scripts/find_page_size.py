from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(root_dir):
    '''
    Traverse the directory and prints the page size.
    '''
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        network_trace_filename = os.path.join(path, 'network_' + url)
        page_request_sizes = get_request_sizes(network_trace_filename, url)
        page_size = sum([size for _, size in page_request_sizes.items()])
        print '{0} {1}'.format(url, page_size)

def get_request_sizes(network_filename, page):
    request_size = dict()
    with open(network_filename, 'rb') as input_file:
        found_root = False
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if not found_root and network_event[METHOD] == 'Network.requestWillBeSent':
                request_url = network_event[PARAMS]['request']['url']
                # print 'request url: {0} page: {1}'.format(request_url, page)
                found_root = common_module.escape_page(request_url) == common_module.escape_page(page)

            if not found_root:
                continue

            request_id = network_event[PARAMS]['requestId']
            if network_event['method'] == 'Network.requestWillBeSent':
                request_size[request_id] = 0
            elif network_event[METHOD] == 'Network.responseReceived':
                status = int(network_event[PARAMS]['response']['status'])
                if status == 403:
                    del request_size[request_id]
            elif network_event['method'] == 'Network.dataReceived':
                if request_id in request_size:
                    request_size[request_id] += network_event['params']['encodedDataLength']
            elif network_event['method'] == 'Network.loadingFinished':
                request_id = network_event['params']['requestId']
                if request_id in request_size:
                    cumulative_size = request_size[request_id]
                    request_size[request_id] = max(network_event['params']['encodedDataLength'], cumulative_size)
    return request_size

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
