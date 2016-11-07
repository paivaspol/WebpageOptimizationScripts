from argparse import ArgumentParser

import common_module
import constants
import os
import simplejson as json

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    for page in pages:

        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            failed_pages.append(page)
            continue

        dependencies = common_module.get_dependencies(dependency_filename, True)
        last_important_dependency_check_time = get_dependency_checked_time(page, \
                                                                           network_filename, \
                                                                           dependencies)
        print '{0} {1}'.format(page, last_important_dependency_check_time)

def get_dependency_checked_time(page, network_filename, dependencies):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        last_request_timestamp = -1
        first_request_timestamp = -1
        result = dict()
        dependencies_request_id = set()
        seen_urls = set()
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
                    and url not in seen_urls \
                    and common_module.is_request_from_scheduler(initiator, page, request_type):
                    dependencies_request_id.add(request_id)
                    seen_urls.add(url)

            elif network_event[constants.METHOD] == 'Network.loadingFinished':
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                if request_id in dependencies_request_id:
                    time_since_first_request = timestamp - first_request_timestamp
                    last_request_timestamp = max(last_request_timestamp, time_since_first_request)

        return last_request_timestamp

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
