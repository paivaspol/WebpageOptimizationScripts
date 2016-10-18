from argparse import ArgumentParser

import common_module
import os
import simplejson as json
import numpy

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'
TYPE = 'type'
INITIATOR = 'initiator'

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = common_module.get_pages(args.page_list)

    failed_pages = []
    for page in pages:

        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')

        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            failed_pages.append(page)
            continue

        # Get the unimportant dependencies
        dependencies = common_module.get_unimportant_dependencies(dependency_filename)
        time_to_first_xhr_request = get_first_unimportant_resource_dependency_request_time_from_scheduler(page, network_filename, dependencies)
        last_unimportant_dependency_request = get_last_unimportant_resource_dependency_request_time(page, network_filename, dependencies)
        # print str(time_to_first_xhr_request) + ' ' + str(last_unimportant_dependency_request)
        if last_unimportant_dependency_request is not None and \
            time_to_first_xhr_request is not None:
            diff = last_unimportant_dependency_request - time_to_first_xhr_request
            print '{0} {1} {2} {3}'.format(page, time_to_first_xhr_request, last_unimportant_dependency_request, diff)

def get_first_unimportant_resource_dependency_request_time_from_scheduler(page, network_filename, dependencies):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        first_request_timestamp = -1
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]
                request_type = network_event[PARAMS][TYPE]
                timestamp = network_event[PARAMS][TIMESTAMP]
                initiator = network_event[PARAMS][INITIATOR]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = timestamp
                    else:
                        continue
        
                if request_type == 'XHR' and url in dependencies and is_request_from_scheduler(initiator, page):
                    return timestamp - first_request_timestamp

def get_last_unimportant_resource_dependency_request_time(page, network_filename, dependencies):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        last_request_timestamp = -1
        first_request_timestamp = -1
        seen_urls = set()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]
                request_type = network_event[PARAMS][TYPE]
                timestamp = network_event[PARAMS][TIMESTAMP]
                initiator = network_event[PARAMS][INITIATOR]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = timestamp
                    else:
                        continue
        
                if url in dependencies and url not in seen_urls:
                    seen_urls.add(url)
                    if timestamp > last_request_timestamp:
                        last_request_timestamp = timestamp
                        # print '\t{0} {1}'.format(url, last_request_timestamp - first_request_timestamp)
        return last_request_timestamp - first_request_timestamp

def is_request_from_scheduler(initiator_obj, page):
    initiator_type = initiator_obj[TYPE]
    callframes = initiator_obj['stack']['callFrames']
    if len(callframes) != 1:
        return False
    url = callframes[0][URL]
    function_name = callframes[0]['functionName']
    return initiator_type == 'script' and common_module.escape_page(url) == page and (function_name == 'important_url_handler' or len(function_name) == 0)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
