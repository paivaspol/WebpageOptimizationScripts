from argparse import ArgumentParser

import simplejson as json

METHOD = 'method'
PARAMS = 'params'
INITIATOR = 'initiator'
REQUEST_HEADERS = 'requestHeaders'
REFERER = 'referer'

def find_initiator(network_filename):
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                print network_event[PARAMS]['documentURL'] + ' ' + network_event[PARAMS]['request']['url']
            # if network_event[METHOD] == 'Network.responseReceived':
            #     response = network_event['params']['response']
            #     if REQUEST_HEADERS in response and REFERER in response[REQUEST_HEADERS]:
            #             print response[REQUEST_HEADERS][REFERER]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    find_initiator(args.network_filename)
