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
    counter = 0
    total_count = 0
    for page in pages:
        # if page in page_set:
        if process_page(root_dir, page):
            counter += 1
        total_count += 1
    print 'Result: ' + str(counter) + '/' + str(total_count)

def process_page(root_dir, page):
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not (os.path.exists(network_filename) and os.path.exists(request_id_to_url_filename)):
        return
    filetype_histogram = defaultdict(list)
    with open(request_id_to_url_filename, 'rb') as input_file:
        # for raw_line in input_file:
        #     line = raw_line.strip().split()
        #     if len(line) != 2:
        #         continue
        #     request_id, url = line
        #     domain = common_module.extract_domain(url)
        # print '{0} {1}'.format(page, len(domain_to_children.keys()))

        if process_network_file(network_filename, page, filetype_histogram):
            print page + ' Yes'
            return True
        else:
            print page + ' No'
            return False


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
                request_url = network_event[PARAMS]['request']['url']
                parsed_url = urlparse(request_url)
                if 'require' in parsed_url.path:
                    print request_url
                    return True
    return False

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_directories(args.root_dir)
