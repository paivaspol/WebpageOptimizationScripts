from argparse import ArgumentParser

import simplejson as json

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
INITIATOR = 'initiator'
REQUEST = 'request'
RESPONSE = 'response'
REQUEST_HEADERS = 'requestHeaders'
REFERER = 'referer'
URL = 'url'
STACKTRACE = 'stackTrace'
TYPE = 'type'

DEFAULT_REQUESTER = '##default'

def find_initiator(network_filename):
    with open(network_filename, 'rb') as input_file:
        req_id_to_request_obj = dict()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            # if network_event[METHOD] == 'Network.requestWillBeSent':
            #     print network_event[PARAMS]['documentURL'] + ' ' + network_event[PARAMS]['request']['url']

            if network_event[METHOD] == 'Network.requestWillBeSent':
                request_id = network_event[PARAMS][REQUEST_ID]
                req_id_to_request_obj[request_id] = network_event
            if network_event[METHOD] == 'Network.responseReceived':
                response = network_event['params']['response']
                request_id = network_event[PARAMS][REQUEST_ID]
                request = req_id_to_request_obj[request_id]
                initiator = request[PARAMS][INITIATOR]
                if REQUEST_HEADERS in response and REFERER in response[REQUEST_HEADERS]:
                    print 'referer: {0} initiator: {1}\n'.format(response[REQUEST_HEADERS][REFERER], initiator)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    find_initiator(args.network_filename)
