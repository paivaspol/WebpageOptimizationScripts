from argparse import ArgumentParser 

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
    if args.page_list is not None:
        pages = common_module.get_pages(args.page_list)

    failed_pages = []
    times_to_first_byte = []
    for page in pages:
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            failed_pages.append(page)
            continue
        dependencies = common_module.get_dependencies(dependency_filename)
        times_to_first_byte.extend(get_times_to_first_byte(page, network_filename, dependencies))
    times_to_first_byte.sort()
    for time in times_to_first_byte:
        print time

def get_times_to_first_byte(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        times_to_first_byte = []
        found_first_request = False
        first_request_timestamp = -1
        dependency_request_id_to_request_sent_timestamp = dict()
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
                    # We have already discovered all the dependencies.
                    # Get the current timestamp and find the time difference.
                    timestamp = network_event[PARAMS][TIMESTAMP]
                    dependency_request_id_to_request_sent_timestamp[request_id] = timestamp

                    dependencies.remove(url)
            elif network_event[METHOD] == 'Network.dataReceived':
                if request_id in dependency_request_id_to_request_sent_timestamp:
                    request_timestamp = dependency_request_id_to_request_sent_timestamp[request_id]
                    first_byte_timestamp = network_event[PARAMS][TIMESTAMP]
                    times_to_first_byte.append(first_byte_timestamp - request_timestamp)
                    
                if len(dependencies) == 0:
                    break
        return times_to_first_byte

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
