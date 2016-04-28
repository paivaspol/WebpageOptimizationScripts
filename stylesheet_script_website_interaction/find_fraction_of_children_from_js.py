from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import simplejson as json

DIRECTORY = 'apple-pi.eecs.umich.edu_grouped_domain_script_execution_{0}_{1}'
PARAMS = 'params'
METHOD = 'method'
REQUEST = 'request'

# Javascript Constants
INITIATOR = 'initiator'
TYPE = 'type'
SCRIPT = 'script'
STACK_TRACE = 'stackTrace'
URL = 'url'

def process_directories(root_dir, experiment_result_root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        process_page(root_dir, experiment_result_root_dir, page)

def process_page(root_dir, experiment_result_root_dir, page):
    page_to_domain_mapping_filename = os.path.join(root_dir, page, 'page_id_to_domain_mapping.txt')
    if not os.path.exists(page_to_domain_mapping_filename):
        return
    total_js_children = 0
    same_domain_js_children = 0
    cross_domain_js_children = 0
    page_to_domain_mapping = common_module.parse_page_id_to_domain_mapping(page_to_domain_mapping_filename)
    for page_id, domain in page_to_domain_mapping.iteritems():
        page_filename = page_id + '.html'
        page_directory = DIRECTORY.format(page, page_filename)
        path_to_result = os.path.join(experiment_result_root_dir, '0', page_directory)
        network_filename = os.path.join(path_to_result, 'network_' + page_directory)
        if not os.path.exists(network_filename):
            continue
        children_from_js, all_requests = process_network_file(network_filename, page, page_filename)
        if domain == page:
            same_domain_js_children += len(children_from_js)
        else:
            cross_domain_js_children += len(children_from_js)
        total_js_children += len(children_from_js)
    if total_js_children > 0:
        print '{0} {1} {2} {3}'.format(page, same_domain_js_children, cross_domain_js_children, total_js_children)

def process_network_file(network_filename, page, subpage):
    first_request = DIRECTORY.format(page, subpage)
    children_from_js = set()
    seen_in_will_be_sent = set()
    all_requests = set()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if not found_first_request and \
                network_event[METHOD] == 'Network.requestWillBeSent':
                if common_module.escape_page(network_event[PARAMS][REQUEST]['url']) \
                    == first_request:
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
                            children_from_js.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                all_requests.add(network_event[PARAMS]['requestId'])
    all_requests = all_requests & seen_in_will_be_sent
    real_children_from_js = children_from_js & all_requests
    return real_children_from_js, all_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('experiment_result_root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_directories(args.root_dir, args.experiment_result_root_dir)
