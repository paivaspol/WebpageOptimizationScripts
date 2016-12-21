from argparse import ArgumentParser

import simplejson as json

PARAMS = 'params'
METHOD = 'method'
TIMESTAMP = 'timestamp'
REQUEST_ID = 'requestId'
TIMESTAMP = 'timestamp'

def iterate_network_trace(network_trace_filename):
    current_walltime_will_be_sent = None
    current_walltime_loading_finished = None
    with open(network_trace_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            #print 'network event: ' + str(network_event)
            if network_event[METHOD] == 'Network.requestServedFromCache':
                continue
            this_event_walltime = network_event[PARAMS][TIMESTAMP]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                if current_walltime_will_be_sent is not None and this_event_walltime <= current_walltime_will_be_sent:
                    raise ValueError('We are fucked')
                current_walltime_will_be_sent = float(this_event_walltime)
                # print current_walltime
            elif network_event[METHOD] == 'Network.loadingFinished':
                if current_walltime_loading_finished is not None and this_event_walltime <= current_walltime_loading_finished:
                    raise ValueError('We are fucked - loading Finished')
                current_walltime_loading_finished = float(this_event_walltime)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_trace_filename')
    args = parser.parse_args()
    iterate_network_trace(args.network_trace_filename)

