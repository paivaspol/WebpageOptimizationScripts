from argparse import ArgumentParser 
from collections import defaultdict

import constants
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

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    dependency_load_times = None
    if args.dependency_load_time is not None:
        dependency_load_times = get_dependency_load_times(args.dependency_load_time)
    for page in pages:
        if args.url is not None and args.url not in page:
            continue
        # if 'cbc.ca' not in page:
        #     continue

        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            continue
        dependencies = common_module.get_dependencies(dependency_filename)
        important_request_sizes, type_count = get_important_request_sizes(page, network_filename, dependencies)
        line = '{0} {1} {2}'.format(page, sum(important_request_sizes.values()), len(important_request_sizes))
        if args.dependency_load_time is not None and page in dependency_load_times:
            line += ' {0}'.format(dependency_load_times[page])
        print line

        stats_str = '\t'
        for resource_type in type_count:
            stats_str += '{0} {1}; '.format(resource_type, type_count[resource_type])
        if args.print_resource_type_count:
            print stats_str

def get_important_request_sizes(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        request_count = defaultdict(lambda: 0)
        found_first_request = False
        first_request_timestamp = -1
        found_request_ids = set()
        request_id_to_size = dict()
        request_id_to_url = dict()
        type_count = defaultdict(lambda: 0)
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                # Make sure to find the first request before parsing the file.
                url = network_event[PARAMS][REQUEST][URL]
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = network_event[PARAMS][TIMESTAMP]
                    else:
                        continue
                if url in dependencies:
                    found_request_ids.add(request_id)
                    request_id_to_url[request_id] = url
            elif network_event[METHOD] == 'Network.responseReceived':
                if request_id in found_request_ids and not (network_event[PARAMS][constants.TYPE] == 'Document' \
                    or network_event[PARAMS][constants.TYPE] == 'Script' or network_event[PARAMS][constants.TYPE] == 'Stylesheet'):
                    # Not an important resource.
                   found_request_ids.remove(request_id)
                elif request_id in found_request_ids:
                    type_count[network_event[PARAMS][constants.TYPE]] += 1
            elif network_event[METHOD] == 'Network.loadingFinished':
                if request_id in found_request_ids:
                    request_id_to_size[request_id] = network_event[PARAMS][constants.ENCODED_DATA_LENGTH]
                    # print request_id_to_url[request_id]
        return request_id_to_size, type_count

def get_dependencies(dependency_filename):
    with open(dependency_filename, 'rb') as input_file:
        return { line.strip().split()[2] for line in input_file }

def get_dependency_load_times(dependency_load_time_filename):
    with open(dependency_load_time_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file if not line.startswith('Failed') ]
        return { key: value for key, value in temp }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--url', default=None)
    parser.add_argument('--print-resource-type-count', default=False, action='store_true')
    parser.add_argument('--dependency-load-time', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
