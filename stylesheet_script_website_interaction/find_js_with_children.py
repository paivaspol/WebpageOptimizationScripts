from argparse import ArgumentParser

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

def main(root_dir):
    pages = os.listdir(root_dir)
    scripts_with_children = set()
    for page in pages:
        scripts_with_children |= process_page(root_dir, page)
    
    for script in scripts_with_children:
        print script

def process_page(root_dir, page):
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    unique_scripts = set()
    if os.path.exists(network_filename):
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
                    if INITIATOR in network_event[PARAMS] and \
                        network_event[PARAMS][INITIATOR][TYPE] == SCRIPT and \
                        STACK_TRACE in network_event[PARAMS][INITIATOR]:
                        stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                        if len(stack_trace) > 0:
                            url = stack_trace[0][URL]
                            unique_scripts.add(url)
    return unique_scripts   

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
