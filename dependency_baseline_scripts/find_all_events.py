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

def main(network_event_filename):
    target_url = 'http://a.espncdn.com/redesign/assets/img/logos/logo-espn-82x20@2x.png'
    find_all_requests(network_event_filename, target_url)

def find_all_requests(network_filename, target_url):
    # print dependencies
    request_ids = set()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]
                if url == target_url:
                    print 'RequestWillBeSent: ' + str(request_id) + ' ts: ' + str(network_event[PARAMS][TIMESTAMP])
                    print '\t' + str(network_event[PARAMS][constants.INITIATOR])
            elif network_event[METHOD] == 'Network.responseReceived':
                url = network_event[PARAMS][RESPONSE][URL]
                if url == target_url:
                    print 'Response Received: ' + str(request_id) + ' ts: ' + str(network_event[PARAMS][TIMESTAMP])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_event_filename')
    args = parser.parse_args()
    main(args.network_event_filename)
