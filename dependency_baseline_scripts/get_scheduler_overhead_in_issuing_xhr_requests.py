from argparse import ArgumentParser

import constants
import common_module
import os
import simplejson as json

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    failed_pages = []
    for page in pages:
        if 'espncricinfo.com' not in page:
            continue
        dependency_filename = os.path.join(dependency_dir, \
                                           page, \
                                           'dependency_tree.txt')

        network_filename = os.path.join(root_dir, page, \
                                        'network_' + page)
        if not (os.path.exists(dependency_filename) and \
                os.path.exists(network_filename)):
            failed_pages.append(page)
            continue
        dependencies = common_module.get_dependencies(dependency_filename, \
                                                True) # Get only important resources.

        per_object_overhead = find_scheduler_overhead(network_filename, dependencies, page)
        total_overhead = sum(per_object_overhead.values())
        print '{0} {1}'.format(page, total_overhead)
        output_per_object_overhead(per_object_overhead)

def output_per_object_overhead(per_object_overhead):
    for url, overhead in per_object_overhead.iteritems():
        print '{0} {1}'.format(url, overhead)

def find_scheduler_overhead(network_filename, dependencies, page):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        last_request_timestamp = -1
        first_request_timestamp = -1
        seen_urls = set()
        request_id_to_first_request_timestamp = dict()
        request_id_to_url = dict()
        result = dict()
        for line in input_file:
            network_event = json.loads(json.loads(line.strip()))
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
        
                if url in dependencies \
                    and common_module.is_request_from_scheduler(initiator, page, request_type):
                    request_id_to_first_request_timestamp[request_id] = timestamp
                    request_id_to_url[request_id] = url

            elif network_event[constants.METHOD] == 'Network.loadingFinished':
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                if request_id in request_id_to_first_request_timestamp:
                    start_timestamp = request_id_to_first_request_timestamp[request_id]
                    object_overhead = timestamp - start_timestamp
                    url = request_id_to_url[request_id]
                    result[url] = object_overhead
        return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependencies_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependencies_dir)
