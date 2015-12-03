from argparse import ArgumentParser

import simplejson as json

import os

PARAMS = 'params'
OUTPUT_FILE = 'outstanding_requests.txt'

def find_outstanding_request_during_intervals(chrome_network_filename, utilization_filename, output_dir):
    '''
    Finds an outstanding request during each interval
    '''
    interval_utilizations = parse_utilization_file(utilization_filename)
    requests = parse_network_file(chrome_network_filename)
    result = [] # Number of requests
    interval_size = None
    for interval, utilization in interval_utilizations:
        if interval_size is None:
            # Get the interval size.
            interval_size = interval[1] - interval[0]

        counter = 0
        for i in range(0, len(requests)):
            request = requests[i]
            if (interval[0] <= request[1][0] < interval[1]) or \
                (interval[0] <= request[1][1] < interval[1]) or \
                (request[1][0] < interval[0] < interval[1] < request[1][1]):
                counter += 1
        result.append(counter)
    output_to_file(interval_utilizations, result, interval_size, output_dir)

def output_to_file(interval_utilizations, outstanding_requests_count, interval_size, output_dir):
    '''
    Outputs the results to a file.
    '''
    with open(os.path.join(output_dir, OUTPUT_FILE), 'wb') as output_file:
        for i in range(0, len(interval_utilizations)):
            interval, utilization = interval_utilizations[i]
            num_outstanding_request = outstanding_requests_count[i]
            line = '{0} {1} {2} {3} {4}'.format((i * interval_size), interval[0], interval[1], utilization, num_outstanding_request)
            output_file.write(line + '\n')

def parse_utilization_file(utilization_filename):
    '''
    Parses the utilizations file and return a list containing tuples of intervals and utilization.
    The list is sorted on the start of the interval.
    '''
    result = dict()
    with open(utilization_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            key = int(line[2]), int(line[3])
            value = float(line[1])
            result[key] = value
    return sorted(result.iteritems(), key=lambda x: x[0][0])

def parse_network_file(chrome_network_file):
    '''
    Parsers the chrome network events.
    Returns a dictionary mapping: request id -> (requestWillBeSent, loadingFinished)
    '''
    result = dict() # Mapping: request id --> (requestWillBeSent, loadingFinished)
    timestamp_dict = dict() # Mapping: request id --> timestamp
    with open(chrome_network_file, 'rb') as input_file:
        for raw_line in input_file:
            event = json.loads(json.loads(raw_line.strip()))
            if event['method'] == 'Network.requestWillBeSent':
                request_id, timestamp = get_requestid_and_timestamp(event)
                wallTime = convert_to_ms_precision(float(event[PARAMS]['wallTime']))
                result[request_id] = (wallTime, -1)
                timestamp_dict[request_id] = timestamp
            elif event['method'] == 'Network.loadingFinished' or \
                event['method'] == 'Network.loadingFailed':
                request_id, timestamp = get_requestid_and_timestamp(event)
                if request_id in result:
                    current_wallTime = result[request_id][0] + (timestamp - timestamp_dict[request_id])
                    result[request_id] = (result[request_id][0], current_wallTime)
    sorted_result = sorted(result.iteritems(), key=lambda x: x[1][0])

    return sorted_result

def print_object_duration(requests):
    for request in requests:
        print '{0} {1} {2}'.format(request[0], (request[1][1] - request[1][0]), request)

def print_generic(intervals):
    for interval in intervals:
        print interval

def get_requestid_and_timestamp(event):
    '''
    Extracts the request id and the timestamp from the event.
    '''
    requestId = event[PARAMS]['requestId']
    timestamp = convert_to_ms_precision(float(event[PARAMS]['timestamp']))
    return requestId, timestamp

def convert_to_ms_precision(timestamp):
    '''
    Converts the timestamp to millisecond precision.
    '''
    return timestamp * 1000

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('chrome_network_file')
    parser.add_argument('utilization_filename')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    if os.path.exists(args.chrome_network_file) and \
        os.path.exists(args.utilization_filename):
        find_outstanding_request_during_intervals(args.chrome_network_file, args.utilization_filename, args.output_dir)
    else:
        print 'Chrome found: {0}, utilization found: {1}'.format(os.path.exists(args.chrome_network_file), os.path.exists(args.utilization_filename))
