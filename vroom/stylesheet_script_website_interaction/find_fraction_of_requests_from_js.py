from argparse import ArgumentParser

import common_module
import os
import simplejson as json
import urlparse

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
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        children_from_js, all_requests = find_requests_from_initiator(network_filename, page)
        num_children_from_js = len(children_from_js)
        num_all_requests = len(all_requests)
        # fraction = 1.0 * num_children_from_js / num_all_requests
        # print page + ' ' + str(num_children_from_js) + ' ' + str(num_all_requests) + ' ' + str(fraction)

def find_requests_from_initiator(network_filename, page):
    children_from_js = set()
    same_domain = set()
    external_domain = set()
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
                        request_url = network_event[PARAMS]['request']['url']
                        parsed_url = urlparse.urlparse(request_url)
                        request_id = network_event[PARAMS]['requestId']
                        if args.resource_type is None or \
                            (args.resource_type is not None and args.resource_type in parsed_url.path):
                            children_from_js.add(request_id)
                            if page == common_module.extract_domain(url):
                                same_domain.add(request_id)
                            elif page != common_module.extract_domain(url):
                                external_domain.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                all_requests.add(network_event[PARAMS]['requestId'])
    all_requests = all_requests & seen_in_will_be_sent
    real_children_from_js = children_from_js & all_requests
    same_domain = same_domain & all_requests
    external_domain = external_domain & all_requests
    assert len(same_domain) + len(external_domain) == len(real_children_from_js)
    if len(all_requests) > 0:
        print '{0} {1} {2} {3} {4}'.format(page, len(same_domain), len(external_domain), len(real_children_from_js), len(all_requests))
    return real_children_from_js, all_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--resource-type', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
