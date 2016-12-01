from argparse import ArgumentParser

import constants
import common_module
import os
import simplejson as json
import numpy

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = common_module.get_pages(args.page_list)

    failed_pages = []
    for page in pages:
        if 'abcnews.go.com' not in page:
            continue
        print page

        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')

        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            failed_pages.append(page)
            continue

        # Get the unimportant dependencies
        important_dependencies = common_module.get_dependencies(dependency_filename, True)
        unimportant_dependencies = common_module.get_unimportant_dependencies(dependency_filename)
        print 'important: ' + str(important_dependencies)
        print 'unimportant: ' + str(unimportant_dependencies)
        time_to_first_xhr_request = get_first_unimportant_resource_dependency_request_time_from_scheduler(page, network_filename, unimportant_dependencies)
        last_important_dependency_fetch_time = get_last_dependency_fetch_time(page, network_filename, important_dependencies) # This is the time when all important dependencies have been fetched.
        
        print '{0} {1} {2}'.format(page, time_to_first_xhr_request, last_important_dependency_fetch_time)
        # if last_important_dependency_fetch_time is not None and \
        #     time_to_first_xhr_request is not None:
        #     diff = time_to_first_xhr_request - last_important_dependency_fetch_time
        #     print '{0} {1} {2} {3}'.format(page, time_to_first_xhr_request, last_important_dependency_fetch_time, diff)

def get_first_unimportant_resource_dependency_request_time_from_scheduler(page, network_filename, dependencies):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        first_request_timestamp = -1
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                request_type = network_event[constants.PARAMS][constants.TYPE]
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                initiator = network_event[constants.PARAMS][constants.INITIATOR]

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

def get_last_dependency_fetch_time(page, network_filename, dependencies):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        last_request_timestamp = -1
        first_request_timestamp = -1
        request_id_to_url_map = dict()
        url_seen = set()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                initiator = network_event[constants.PARAMS][constants.INITIATOR]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = timestamp
                    else:
                        continue
                if url not in url_seen and not is_request_from_scheduler(initiator, page):
                    url_seen.add(url)
                    request_id_to_url_map[request_id] = url
                
            elif network_event[constants.METHOD] == 'Network.loadingFinished':
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                url = request_id_to_url_map[request_id]
                if url in dependencies:
                    last_request_timestamp = max(last_request_timestamp, timestamp)
        return last_request_timestamp - first_request_timestamp

def is_request_from_scheduler(initiator_obj, page):
    initiator_type = initiator_obj[constants.TYPE]
    callframes = initiator_obj['stack']['callFrames']
    if len(callframes) != 1:
        return False
    url = callframes[0][constants.URL]
    function_name = callframes[0]['functionName']
    return initiator_type == 'script' and common_module.escape_page(url) == page and (function_name == 'important_url_handler' or len(function_name) == 0)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
