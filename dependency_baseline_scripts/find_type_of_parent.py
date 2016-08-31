from argparse import ArgumentParser 
from collections import defaultdict

import constants
import common_module
import os
import simplejson as json

def main(root_dir, data_filename):
    dependency_data_dict = get_dependencies_dict(data_filename)
    for page in dependency_data_dict:
        print 'Page: ' + page
        network_event_filename = os.path.join(root_dir, page, 'network_' + page)
        urls = dependency_data_dict[page]
        find_all_requests(network_event_filename, urls)

def find_all_requests(network_filename, urls):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
            if network_event[constants.METHOD] == 'Network.responseReceived':
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                headers = network_event[constants.PARAMS][constants.RESPONSE][constants.HEADERS]
                link_header = None
                for header_key in headers.keys():
                    if header_key.lower() == constants.LINK.lower():
                        link_header = header_key

                if link_header is not None:
                    link_header_value = headers[link_header]
                    link_urls = common_module.extract_url_from_link_string(link_header_value)
                    intersection = urls & link_urls
                    url = network_event[constants.PARAMS][constants.RESPONSE][constants.URL]
                    if len(intersection) != 0:
                        # print intersection
                        # print network_event
                        print '\tparent url: ' + url + ' type: ' + network_event[constants.PARAMS][constants.TYPE]
                        request_headers = network_event[constants.PARAMS][constants.RESPONSE][constants.REQUEST_HEADERS]
                        if constants.REFERER in request_headers:
                            referer = network_event[constants.PARAMS][constants.RESPONSE][constants.REQUEST_HEADERS][constants.REFERER]
                            print '\t\tReferer: ' + referer

def get_dependencies_dict(data_filename):
    with open(data_filename, 'rb') as input_file:
        result = defaultdict(set)
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]].add(line[1])
        return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('data_filename')
    args = parser.parse_args()
    main(args.root_dir, args.data_filename)
