from argparse import ArgumentParser 

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
    target_url = 'http://widget-cdn.rpxnow.com/manifest/capture:login?version=1.112.0_widgets_189'
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
                    initiator = network_event[PARAMS]['initiator']
                    print '{0} {1}'.format(request_id, initiator)
                    request_ids.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                if request_id in request_ids:
                    print network_event[PARAMS][RESPONSE]['status']


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_event_filename')
    args = parser.parse_args()
    main(args.network_event_filename)
