from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import simplejson as json

PARAMS = 'params'
METHOD = 'method'
REQUEST = 'request'

# Javascript Constants
INITIATOR = 'initiator'
TYPE = 'type'
SCRIPT = 'script'
STACK_TRACE = 'stackTrace'
URL = 'url'

# page_set = { 'cnet.com', 'espn.com', 'kaspersky.com', 'mydailymoment.com', 'romper.com', 'songlyrics.com' }

def process_directories(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        # if page in page_set:
        process_page(root_dir, page)

def process_page(root_dir, page):
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not (os.path.exists(network_filename) and os.path.exists(request_id_to_url_filename)):
        return
    domain_to_children = dict()
    with open(request_id_to_url_filename, 'rb') as input_file:
        # for raw_line in input_file:
        #     line = raw_line.strip().split()
        #     if len(line) != 2:
        #         continue
        #     request_id, url = line
        #     domain = common_module.extract_domain(url)
        #     domain_to_children[domain] = []
        print '{0} {1}'.format(page, len(domain_to_children.keys()))
        total_requests_sent = process_network_file(network_filename, page, domain_to_children)
        print_histogram(domain_to_children, total_requests_sent)

def print_histogram(domain_to_children, total_requests_sent):
    for domain, children in domain_to_children.iteritems():
        if len(children) > 0:
            fraction = 1.0 * len(children) / total_requests_sent
            print '\t{0} {1} {2} {3}'.format(domain, len(children), total_requests_sent, fraction)
            for child in children:
                print '\t\t{0} {1}'.format(child[0], child[1])

def process_network_file(network_filename, page, domain_to_children):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        request_sent = 0
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if not found_first_request and \
                network_event[METHOD] == 'Network.requestWillBeSent':
                if common_module.escape_page(network_event[PARAMS][REQUEST]['url']) \
                    == page:
                    found_first_request = True
            if not found_first_request:
                continue
            if network_event[METHOD] == 'Network.requestWillBeSent':
                if INITIATOR in network_event[PARAMS] and \
                    network_event[PARAMS][INITIATOR][TYPE] == SCRIPT and \
                    STACK_TRACE in network_event[PARAMS][INITIATOR]:
                    request_sent += 1
                    request_url = network_event[PARAMS]['request']['url']
                    stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                    if len(stack_trace) > 0:
                        url = stack_trace[0][URL]
                        if 'quantserve' in url:
                            request_id = network_event[PARAMS]['requestId']
                            domain = common_module.extract_domain(url)
                            if domain not in domain_to_children:
                                continue
                            domain_to_children[domain].append((request_id, request_url))
        return request_sent

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_directories(args.root_dir)
