from argparse import ArgumentParser

import simplejson as json

METHOD = 'method'
PARAMS = 'params'
INITIATOR = 'initiator'

def find_initiator(network_filename):
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                print str(network_event[PARAMS]['request']['url']) + ' ' + str(network_event[PARAMS][INITIATOR])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    find_initiator(args.network_filename)
