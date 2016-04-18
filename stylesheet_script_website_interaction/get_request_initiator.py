from argparse import ArgumentParser

import common_module
import os
import simplejson as json

PARAMS = 'params'
METHOD = 'method'

# Javascript Constants
INITIATOR = 'initiator'
TYPE = 'type'
SCRIPT = 'script'
STACK_TRACE = 'stackTrace'
URL = 'url'

def process_pages(pages, root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    for page in pages:
        escaped_page = common_module.escape_page(page)
        network_filename = os.path.join(root_dir, escaped_page, \
                'network_' + escaped_page)
        if not os.path.exists(network_filename):
            continue
        initiators = get_initiators(network_filename, page)
        if len(initiators) > 0:
            output_filename = os.path.join(output_dir, escaped_page)
            output_initiators(initiators, output_filename)

def output_initiators(intiators, output_filename):
    with open(output_filename, 'wb') as output_file:
        for initiator in intiators:
            output_file.write('Initiator: ' + initiator[0][URL])
            for stack_trace in initiator:
                output_file.write('\t' + format_initiator(stack_trace) + '\n')

            
def format_initiator(initiator):
    initiator_string = '{0} {1} {2}'.format(initiator[URL], \
                                        initiator['lineNumber'], \
                                        initiator['columnNumber'])
    return initiator_string

def get_initiators(network_filename, page):
    page_domain = common_module.extract_domain(page)
    initiators = list()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                if INITIATOR in network_event[PARAMS] and \
                    TYPE in network_event[PARAMS][INITIATOR] and \
                    network_event[PARAMS][INITIATOR][TYPE] == SCRIPT and \
                    STACK_TRACE in network_event[PARAMS][INITIATOR]:
                    stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                    if len(stack_trace) > 0 and \
                        stack_trace[0][URL].endswith('.js') and \
                        page_domain != common_module.extract_domain(stack_trace[0][URL]):
                        initiators.append(stack_trace)
    return initiators

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_file')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    pages = common_module.parse_pages_file(args.pages_file)
    process_pages(pages, args.root_dir, args.output_dir)
