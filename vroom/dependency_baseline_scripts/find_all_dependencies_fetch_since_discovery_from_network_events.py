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

        dependencies = common_module.get_dependencies(dependency_filename, args.only_important_resources)
        dependency_finish_download_time = get_dependency_finish_download_time(page, \
                                                                              network_filename, \
                                                                              dependencies)
        print '{0} {1}'.format(page, dependency_finish_download_time)

def output_to_file(output_dir, filename, dependency_finish_load_times):
    output_filename = os.path.join(output_dir, filename)
    with open(output_filename, 'wb') as output_file:
        for url, dependency_finish_load_time in dependency_finish_load_times.iteritems():
            output_file.write('{0} {1}\n'.format(url, dependency_finish_load_time))

def get_dependency_finish_download_time(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        first_request_timestamp = -1
        discovery_times = dict()
        finish_loading_times = dict()
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except Exception:
                network_event = json.loads(raw_line.strip())
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]

                # if 'redirectResponse' in network_event[PARAMS]:
                #     url = network_event[PARAMS]['redirectResponse']['url']

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
                    time_since_first_request = timestamp - first_request_timestamp
                    discovery_times[request_id] = time_since_first_request
                    dependencies.remove(url)

            elif found_first_request and network_event[METHOD] == 'Network.loadingFinished' or \
                    found_first_request and network_event[METHOD] == 'Network.loadingFailed':

                request_id = network_event[PARAMS][REQUEST_ID]
                if request_id in discovery_times:
                    # We have already discovered all the dependencies.
                    # Get the current timestamp and find the time difference.
                    finish_timestamp = network_event[PARAMS][TIMESTAMP]
                    time_from_first_request = finish_timestamp - first_request_timestamp
                    finish_loading_times[request_id] = time_from_first_request

        intersection = set(discovery_times.keys()) & set(finish_loading_times.keys())
        max_discovery_time = -1
        max_fetch_time = -1
        for request_id in intersection:
            max_discovery_time = max(max_discovery_time, discovery_times[request_id])
            max_fetch_time = max(max_fetch_time, finish_loading_times[request_id])
        return max_fetch_time - max_discovery_time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--only-important-resources', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
