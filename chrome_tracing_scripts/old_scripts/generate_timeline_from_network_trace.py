from argparse import ArgumentParser

import simplejson as json

PARAMS = 'params'
METHOD = 'method'
TIMESTAMP = 'timestamp'
REQUEST_ID = 'requestId'
WALLTIME = 'wallTime'

def iterate_network_trace(network_trace_filename):
    request_timestamp_dict = dict()
    request_start_walltime_dict = dict()
    request_finished_relative_times = []
    request_data_received = []
    with open(network_trace_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[METHOD] == 'Network.requestWillBeSent':
                request_timestamp_dict[network_event[PARAMS][REQUEST_ID]] = network_event[PARAMS][TIMESTAMP]
                request_start_walltime_dict[network_event[PARAMS][REQUEST_ID]] = network_event[PARAMS][WALLTIME]
            elif network_event[METHOD] == 'Network.dataReceived':
                request_data_received.append(network_event[PARAMS][TIMESTAMP])
            elif network_event[METHOD] == 'Network.loadingFinished':
                request_finished_relative_times.append(network_event[PARAMS][TIMESTAMP])
    min_timestamp = print_request_timestamps(request_timestamp_dict, 'RequestWillBeSent', 0.25)
    print_timestamps(request_finished_relative_times, min_timestamp, 'RequestFinished', 0.5)
    print_timestamps(request_data_received, min_timestamp, 'DataReceived', 0.75)

def print_request_timestamps(request_timestamp_dict, label, index_value):
    sorted_request_timestamps = sorted(request_timestamp_dict.values())
    for timestamp in sorted_request_timestamps:
        time_delta = timestamp - sorted_request_timestamps[0]
        line = '{0} {1} {2}'.format(index_value, label, time_delta)
        print line
    return sorted_request_timestamps[0]

def print_timestamps(timestamps, min_timestamp, label, index_value):
    for timestamp in timestamps:
        time_delta = timestamp - min_timestamp
        line = '{0} {1} {2}'.format(index_value, label, time_delta)
        print line

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_trace_filename')
    args = parser.parse_args()
    iterate_network_trace(args.network_trace_filename)

