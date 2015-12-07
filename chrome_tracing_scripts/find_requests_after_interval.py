from argparse import ArgumentParser

import os

import common_module

PARAMS = 'params'
OUTPUT_FILE = 'requests_after_interval.txt'

def find_outstanding_request_during_intervals(chrome_network_filename, utilization_filename, output_dir):
    '''
    Finds an outstanding request during each interval
    '''
    intervals = parse_interval_file(utilization_filename)
    requests = common_module.parse_network_file(chrome_network_filename)
    result = [] # Number of requests
    interval_size = None
    for interval in intervals:
        if interval_size is None:
            # Get the interval size.
            interval_size = interval[1] - interval[0]

        counter = 0
        for i in range(0, len(requests)):
            request = requests[i]
            if request[1][0] > interval[1]:
                # The request is initiated after this interval.
                counter += 1
        result.append(counter)
    print 'result len: ' + str(len(result))
    output_to_file(intervals, result, requests, interval_size, output_dir)

def output_to_file(interval_utilizations, outstanding_requests_count, requests, interval_size, output_dir):
    '''
    Outputs the results to a file.
    '''
    with open(os.path.join(output_dir, OUTPUT_FILE), 'wb') as output_file:
        for i in range(0, len(interval_utilizations)):
            interval = interval_utilizations[i]
            num_outstanding_request = outstanding_requests_count[i]
            line = '{0} {1:f} {2:f} {3} {4}'.format((i * interval_size), interval[0], interval[1], num_outstanding_request, len(requests))
            output_file.write(line + '\n')


def print_object_duration(requests):
    for request in requests:
        print '{0} {1} {2}'.format(request[0], (request[1][1] - request[1][0]), request)

def print_generic(intervals):
    for interval in intervals:
        print interval

def parse_interval_file(interval_filename):
    result = []
    with open(interval_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.append((float(line[0]), float(line[1])))
    return result

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

