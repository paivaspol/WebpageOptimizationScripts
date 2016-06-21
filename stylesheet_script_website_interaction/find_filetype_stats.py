from argparse import ArgumentParser
from urlparse import urlparse
from collections import defaultdict

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
        process_page(root_dir, page)

def process_page(root_dir, page):
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not (os.path.exists(network_filename) and os.path.exists(request_id_to_url_filename)):
        return
    filetype_histogram = defaultdict(set)
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) != 2:
                continue
            request_id, url = line
            domain = common_module.extract_domain(url)
        print '{0}'.format(page)
        process_network_file(network_filename, page, filetype_histogram)
        if args.with_url:
            print_histogram(filetype_histogram)
        else:
            print_data_for_bar_chart(filetype_histogram)

def print_data_for_bar_chart(domain_to_children):
    total_children = sum( len(children) for _, children in domain_to_children.iteritems() )
    for domain, children in domain_to_children.iteritems():
        fraction = 1.0 * len(children) / total_children
        print '\t{0} {1} {2} {3}'.format(domain, len(children), total_children, fraction)

def print_histogram(domain_to_children):
    for domain, children in domain_to_children.iteritems():
        if len(children) > 0:
            print '\t{0} {1}'.format(domain, len(children))
            for child in children:
                print '\t\t{0} {1}'.format(child[0], child[1])

def process_network_file(network_filename, page, filetype_histogram):
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
                    request_url = network_event[PARAMS]['request']['url']
                    stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                    if len(stack_trace) > 0:
                        url = stack_trace[0][URL]
                        if url == '':
                            continue

                        parsed_url = urlparse(request_url)
                        parsed_initiator_url = urlparse(url)
                        request_id = network_event[PARAMS]['requestId']

                        # print url
                        # print parsed_initiator_url.path
                        if args.only_inline_scripts or args.only_included_scripts:
                            if args.only_inline_scripts and ('.js' in parsed_initiator_url.path or \
                                '.html' in parsed_initiator_url.path or '.php' in parsed_initiator_url.path):
                                continue
                            elif args.only_included_scripts and not ('.js' in parsed_initiator_url.path or \
                                '.html' in parsed_initiator_url.path or '.php' in parsed_initiator_url.path):
                                continue

                        if parsed_url.path.endswith('.js'):
                            # print 'request: ' + request_url + ' initiator: ' + url
                            filetype_histogram['.js'].add((request_url, url))
                        elif '.css' in parsed_url.path:
                            filetype_histogram['.css'].add((request_url, url))
                        elif '.jpg' in parsed_url.path or '.png' in parsed_url.path or \
                            '.gif' in parsed_url.path or '.jpeg' in parsed_url.path:
                            filetype_histogram['image'].add((request_url, url))
                        elif '.html' in parsed_url.path or '.php' in parsed_url.path or \
                            '.asp' in parsed_url.path:
                            filetype_histogram['iframe'].add((request_url, url))
                        else:
                            filetype_histogram['other requests'].add((request_url, url))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--only-inline-scripts', action='store_true', default=False)
    parser.add_argument('--only-included-scripts', action='store_true', default=False)
    parser.add_argument('--with-url', action='store_true')
    args = parser.parse_args()
    process_directories(args.root_dir)
