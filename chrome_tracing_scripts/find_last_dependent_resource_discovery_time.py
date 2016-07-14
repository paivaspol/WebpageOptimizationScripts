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
    # print str(page_dependent_resources.keys()) + ' ' + str(len(page_dependent_resources.keys()))

    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename) or page not in page_dependent_resources:
            # print 'page'
            continue
        dependent_resources = page_dependent_resources[page]
        timestamp_diff, walltime_diff = process_network_file(network_filename, dependent_resources, page)
        if timestamp_diff != -1 and walltime_diff != -1:
            print '{0} {1}'.format(page, timestamp_diff)
        # break

def process_network_file(network_filename, dependent_resources, page):
    dependent_resource_copy = set(dependent_resources)
    # print 'before: ' + str(dependent_resource_copy)
    with open(network_filename, 'rb') as input_file:
        first_request_id = None
        first_request_timestamp = None
        first_request_walltime = None
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if 'requestId' in network_event['params']:
                request_id = network_event['params']['requestId']               
                if network_event['method'] == 'Network.requestWillBeSent':
                    url = network_event['params']['request']['url']
                    # if 'monetate.net' in url:
                    #     print 'url: ' + str(urlparse(url))
                    timestamp = network_event['params']['timestamp']
                    walltime = network_event['params']['wallTime']
                    if common_module.escape_page(url) == page:
                        first_request_id = request_id
                        first_request_timestamp = timestamp
                        first_request_walltime = walltime
                    parsed_url = urlparse(url)
                    if parsed_url.path.endswith('.css') or parsed_url.path.endswith('.js') or \
                        parsed_url.path.endswith('.html'):
                        url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
                    if url in dependent_resource_copy:
                        dependent_resource_copy.remove(url)
                    if len(dependent_resource_copy) == 0:
                        timestamp_diff = timestamp - first_request_timestamp
                        walltime_diff = walltime - first_request_walltime
                        return timestamp_diff, walltime_diff
    # print 'after: ' + str(dependent_resource_copy)
    return -1, -1

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
                parsed_url = urlparse(url)
                if parsed_url.path.endswith('.css') or parsed_url.path.endswith('.js') or \
                    parsed_url.path.endswith('.html'):
                    dependent_resource = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
                else:
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
