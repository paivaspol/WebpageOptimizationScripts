from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import os
import simplejson as json

def main(root_dir, dependency_dir):
    page_dependent_resources = get_dependent_resources(dependency_dir)
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)

    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.join(network_filename):
            continue
        dependent_resources = page_dependent_resources[page]
        request_histogram = process_network_file(network_filename, page)
        print_request_histogram(page, request_histogram, dependent_resources)

def print_request_histogram(page, request_histogram, dependent_resources):
    print page
    for url in request_histogram:
        if url in dependent_resources:
            print '\t{0} {1}'.format(url, request_histogram[url])

def process_network_file(network_filename, page):
    request_histogram = defaultdict(lambda: 0)
    request_id_to_url = dict()
    with open(network_filename, 'rb') as input_file:
        first_request_id = None
        request_ts = None
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if 'requestId' in network_event['params']:
                request_id = network_event['params']['requestId']
                if network_event['method'] == 'Network.requestWillBeSent':
                    url = network_event['params']['request']['url']
                    # print url
                    request_histogram[url] += 1
                    request_id_to_url[request_id] = url
                # elif network_event['method'] == 'Network.loadingFinished':
                #     if request_id == first_request_id:
                #         timestamp = float(network_event['params']['timestamp'])
                #         html_load_time = timestamp - request_ts
                #         return html_load_time
                elif network_event['method'] == 'Network.requestServedFromCache':
                    print request_id_to_url[request_id]
    return request_histogram

def get_dependent_resources(dependency_dir):
    page_dependent_resources = defaultdict(set)
    pages = os.listdir(dependency_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)

    for page in pages:
        dependency_tree_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not os.path.exists(dependency_tree_filename):
            continue
        with open(dependency_tree_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                url = line[2]
                dependent_resource = line[2]
                page_dependent_resources[page].add(dependent_resource)
    return page_dependent_resources

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
