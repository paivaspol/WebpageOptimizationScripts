from argparse import ArgumentParser 
from collections import defaultdict

import common_module
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'
INITIATOR = 'initiator'

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            continue
        dependencies = common_module.get_dependencies(dependency_filename)
        dependency_finish_download_time = get_request_counts(page, network_filename, dependencies)
        print '{0}'.format(page)
        for url, initiator_pair in dependency_finish_download_time.iteritems():
            print '\t{0} {1} {2}'.format(url, initiator_pair[0], initiator_pair[1])

def get_request_counts(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        request_count = defaultdict(lambda: 0)
        found_first_request = False
        first_request_timestamp = -1
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = network_event[PARAMS][TIMESTAMP]
                    else:
                        continue
                if url in dependencies:
                    initiator = network_event[PARAMS][INITIATOR]
                    initiator_type = network_event[PARAMS][INITIATOR]['type']
                    if 'lineNumber' in network_event[PARAMS][INITIATOR]:
                        line_number = network_event[PARAMS][INITIATOR]['lineNumber']
                    else:
                        line_number = -1
                    request_count[url] = (initiator_type, line_number)
        return request_count

def get_dependencies(dependency_filename):
    with open(dependency_filename, 'rb') as input_file:
        return { line.strip().split()[2] for line in input_file }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
