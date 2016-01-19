from argparse import ArgumentParser

import simplejson as json

PARAMS = 'params'
METHOD = 'method'
TIMESTAMP = 'timestamp'
REQUEST_ID = 'requestId'
TIMESTAMP = 'timestamp'

def iterate_network_trace(network_trace_filename):
    current_walltime = None
    with open(network_trace_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                this_event_walltime = network_event[PARAMS][TIMESTAMP]
                if current_walltime is not None and this_event_walltime <= current_walltime:
                    raise ValueError('We are fucked')
                current_walltime = float(this_event_walltime)
                print current_walltime

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_trace_filename')
    args = parser.parse_args()
    iterate_network_trace(args.network_trace_filename)

