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

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        process_page(root_dir, page)

def process_page(root_dir, page):
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not os.path.exists(network_filename):
        return
    js_children, same_domain_js, external_domain_js, all_requests = process_network_file(network_filename, page)
    print '{0} {1} {2} {3} {4}'.format(page, len(same_domain_js), len(external_domain_js), len(js_children), len(all_requests))

def process_network_file(network_filename, page):
    children_from_js = set()
    same_domain_js = set()
    external_domain_js = set()
    seen_in_will_be_sent = set()
    all_requests = set()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
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
                seen_in_will_be_sent.add(network_event[PARAMS]['requestId'])
                if INITIATOR in network_event[PARAMS] and \
                    network_event[PARAMS][INITIATOR][TYPE] == SCRIPT and \
                    STACK_TRACE in network_event[PARAMS][INITIATOR]:
                    stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                    if len(stack_trace) > 0:
                        url = stack_trace[0][URL]
                        parsed_url = urlparse(url)
                        if '.js' in parsed_url.path:
                            request_id = network_event[PARAMS]['requestId']
                            if common_module.extract_domain(url) != page:
                                external_domain_js.add(request_id)
                            else:
                                same_domain_js.add(request_id)
                            children_from_js.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                all_requests.add(network_event[PARAMS]['requestId'])
    all_requests = all_requests & seen_in_will_be_sent
    real_children_from_js = children_from_js & all_requests
    same_domain_js = same_domain_js & all_requests
    external_domain_js = external_domain_js & all_requests
    return real_children_from_js, same_domain_js, external_domain_js, all_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
