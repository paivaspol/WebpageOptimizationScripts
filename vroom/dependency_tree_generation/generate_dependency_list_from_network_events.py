'''
Generates dependency list for each website using the network events.
The dependency list here will return all descedants of a parent up to
the next iframe (Document) type.
'''
from argparse import ArgumentParser
from collections import defaultdict

import common_module
import os
import simplejson as json

def main(page_load_root_dir):
    pages = os.listdir(page_load_root_dir)
    for page in pages:
        if 'nhl.com' not in page:
            continue
        network_filename = os.path.join(page_load_root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        dependency_graph = generate_dependency_graph(network_filename, page)

def generate_dependency_graph(network_filename, page):
    '''
    Each dependency line is defined as [parent] [junk] [url] [index] [type]
    '''
    dependency_graph = populate_mapping_key(network_filename)
    url_to_request_id = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.requestWillBeSent':
                request_id = network_event['params']['requestId']
                resource_type = network_event['params']['type']
                url = network_event['params']['request']['url']
                parent_url = network_event['params']['documentURL'] if 'documentURL' in network_event['params'] else 'about:blank'
                if parent_url == 'about:blank' or parent_url not in dependency_graph:
                    # Special case. Use Referer instead
                    parent_url = network_event['params']['request']['headers']['Referer']
                if common_module.escape_url(url) != page:
                    dependency_graph[parent_url].append(url)
    return dependency_graph

def populate_mapping_key(network_filename):
    result = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.responseReceived':
                resource_type = network_event['params']['type']
                url = network_event['params']['response']['url']
                if resource_type == 'Document':
                    result[url] = []
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_load_root_dir')
    args = parser.parse_args()
    main(args.page_load_root_dir)
