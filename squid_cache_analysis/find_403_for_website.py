from argparse import ArgumentParser

import common_module
import os
import simplejson as json

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
PARAMS = 'params'
METHOD = 'method'
DOCUMENT_URL = 'documentURL'
LOADER_ID = 'requestId'

def find_failed_pages(root_dir, pages, output_unloadable_resources):
    result = []
    for page in pages:
        url = common_module.escape_page(page)
        directory_path = os.path.join(root_dir, url)
        if os.path.exists(directory_path):
            network_filename = os.path.join(directory_path, 'network_' + url)
            if not os.path.exists(network_filename):
                continue
            network_events = parse_network_events(network_filename)
            #print page
            result_find_if_load_failed = find_if_load_failed(network_events, page)
            if result_find_if_load_failed is not None:
                num_403, total_resources, ratio, unloadable_resources = result_find_if_load_failed
                if output_unloadable_resources is not None:
                    write_unloadable_resources(url, unloadable_resources)
                if total_resources > 10:
                    result.append((page, num_403, total_resources, ratio))
            else:
                continue

    sorted_result = sorted(result, key=lambda x: x[3])
    print '# Page Total_resources num_403 ratio'
    for page, num_403, total_resources, ratio in sorted_result:
        print '{0} {1} {2} {3}'.format(page, total_resources, num_403, ratio)

def write_unloadable_resources(url, unloadable_resources, output_dir='./unloadable_resources'):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_path = os.path.join(output_dir, url + '.txt')
    with open(output_path, 'wb') as output_file:
        for resource, method in unloadable_resources:
            output_file.write(resource + ' ' + str(method) + '\n')

def find_if_load_failed(network_events, page):
    page_loader_id = None
    total_count = 0
    counter = 0
    found_root = False
    unloadable_resources = []
    request_dictionary = dict()
    for network_event in network_events:
        if not found_root and network_event[METHOD] == 'Network.requestWillBeSent':
            request_url = network_event[PARAMS]['request']['url']
            found_root = request_url == page

        if not found_root:
            continue

        if network_event[METHOD] == 'Network.requestWillBeSent':
            request_id = network_event[PARAMS]['requestId']
            request_dictionary[request_id] = network_event
        elif network_event[METHOD] == 'Network.responseReceived':
            status = network_event[PARAMS]['response']['status']
            # print network_event[PARAMS]['response'].keys()
            request_id = network_event[PARAMS]['requestId']
            if request_id in request_dictionary:
                request_event = request_dictionary[request_id]
                method = request_event[PARAMS]['request']['method']
                if int(status) == 403 and method == 'GET':
                    # Found the response to the page.
                    unloadable_resources.append((network_event[PARAMS]['response']['url'], method))
                total_count += 1
    if total_count != 0:
        return len(unloadable_resources), total_count, (1.0 * len(unloadable_resources) / total_count), unloadable_resources
    else:
        return None

def parse_network_events(network_events_filename):
    network_events = []
    with open(network_events_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            network_events.append(json.loads(json.loads(line)))
    return network_events

def parse_pages(pages_filename):
    '''
    Parses the pages file.
    '''
    pages = []
    with open(pages_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            pages.append(line[len(line) - 1])
    return pages

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_filename')
    parser.add_argument('--output-unloadable-resources', default=False, action='store_true')
    args = parser.parse_args()
    pages = parse_pages(args.pages_filename)
    find_failed_pages(args.root_dir, pages, args.output_unloadable_resources)
