from argparse import ArgumentParser
from collections import defaultdict

import common_module
import constants
import os
import simplejson as json

def main(root_dir, dependency_dir, output_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not(os.path.exists(network_filename) and \
            os.path.exists(dependency_filename)):
            continue

        children_map, parent_set = get_children_map(dependency_filename)
        # print children_map
        discovery_times = get_discovery_time(children_map, \
                                            parent_set, \
                                            network_filename, \
                                            page)
        output_to_file(output_dir, page, discovery_times)

def output_to_file(output_dir, page, discovery_times):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        sorted_discovery_times = sorted(discovery_times.iteritems(), \
                                        key=lambda x: x[1])
        for resource, discovery_time in sorted_discovery_times:
            output_file.write('{0} {1}\n'.format(resource, discovery_time))

def get_discovery_time(children_map, parent_set, network_filename, page):
    result = dict()
    found_first_request = False
    first_request_timestamp = -1
    parent_fetch_time = dict()
    request_id_to_url = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[constants.PARAMS][constants.REQUEST_ID]

            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = timestamp
                    else:
                        continue
                
                if url in children_map and url not in result:
                    parent = children_map[url]
                    # print 'url: {0} parent: {1}'.format(url, parent)
                    if parent in parent_fetch_time:
                        time_since_parent_fetch_time = \
                            timestamp - parent_fetch_time[parent]
                        result[url] = time_since_parent_fetch_time
                        
                        if len(result) == len(children_map):
                            break

                elif url in parent_set:
                    request_id_to_url[request_id] = url

            elif network_event[constants.METHOD] == 'Network.responseReceived':
                if request_id in request_id_to_url:
                    timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                    parent_fetch_time[url] = timestamp
    # print request_id_to_url
    return result

def get_children_map(dependency_filename):
    children_map = defaultdict(set)
    parent_set = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parent = line[0]
            resource = line[2]
            parent_set.add(parent)
            children_map[resource] = parent
    return children_map, parent_set

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir, args.output_dir)
