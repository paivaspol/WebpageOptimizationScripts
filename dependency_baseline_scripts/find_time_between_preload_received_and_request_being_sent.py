from argparse import ArgumentParser 

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
HEADERS = 'headers'
LINK = 'Link'

def main(root_dir):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = common_module.get_pages(args.page_list)

    failed_pages = []
    all_time_differences = []
    for page in pages:
        # if 'nba.com' not in page:
        #     continue

        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            failed_pages.append(page)
            continue
        time_differences = get_time_between_preload_received_and_request_sent(page, \
                                                                              network_filename)
        all_time_differences.extend(time_differences)
    all_time_differences.sort(key=lambda x: x[2])
    for time_difference in all_time_differences:
        print '{0} {1} {2}'.format(time_difference[0], time_difference[1], time_difference[2])
    print 'Failed Pages: ' + str(failed_pages)

def get_time_between_preload_received_and_request_sent(page, network_filename):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        first_request_timestamp = -1
        url_to_preload_received_timestamp = dict()
        result = []
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]
                event_timestamp = network_event[PARAMS][TIMESTAMP]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = network_event[PARAMS][TIMESTAMP]
                    else:
                        continue

                if url in url_to_preload_received_timestamp and \
                    network_event[PARAMS][constants.INITIATOR][constants.TYPE].lower() == 'parser':
                    # print url + ' ' + str(event_timestamp) + ' ' + str(url_to_preload_received_timestamp[url])
                    time_difference = event_timestamp - url_to_preload_received_timestamp[url]
                    result.append((page, url, time_difference))
                    del url_to_preload_received_timestamp[url]

            elif network_event[METHOD] == 'Network.responseReceived':
                # First, look for Link headers in the headers.
                headers = network_event[PARAMS][RESPONSE][HEADERS]
                timestamp = network_event[PARAMS][TIMESTAMP]
                link_header = None
                for header_key in headers.keys():
                    if LINK.lower() == header_key or \
                        LINK == header_key:
                        link_header = header_key
                if link_header is not None:
                    link_header_value = headers[link_header]
                    urls = common_module.extract_url_from_link_string(link_header_value)
                    for url in urls:
                        url_to_preload_received_timestamp[url] = timestamp
        return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    main(args.root_dir)
