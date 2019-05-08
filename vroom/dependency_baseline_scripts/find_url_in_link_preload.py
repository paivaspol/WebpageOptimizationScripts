from argparse import ArgumentParser 

import constants
import common_module
import os
import simplejson as json

def main(network_event_filename):
    target_url = 'http://fingfx.thomsonreuters.com/gfx/rngs/OLYMPICS-RIO-MEDALS/0100211R2KD/img/thelogo.png'
    find_all_requests(network_event_filename, target_url)

def find_all_requests(network_filename, target_url):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if url == target_url:
                    print 'Request: ' + str(url) + ' ' + str(timestamp)
                    initiator = network_event[constants.PARAMS][constants.INITIATOR]
                    print '\t' + str(initiator)
                
            elif network_event[constants.METHOD] == 'Network.responseReceived':
                timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                headers = network_event[constants.PARAMS][constants.RESPONSE][constants.HEADERS]
                link_header = None
                for header_key in headers.keys():
                    if header_key.lower() == constants.LINK.lower():
                        link_header = header_key

                if link_header is not None:
                    link_header_value = headers[link_header]
                    urls = common_module.extract_url_from_link_string(link_header_value)
                    if target_url in urls:
                        print 'Response: ' + url + ' ' + str(timestamp)
                        print '\t' + str(urls)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_event_filename')
    args = parser.parse_args()
    main(args.network_event_filename)
