from argparse import ArgumentParser

import os

import common_module

PARAMS = 'params'
OUTPUT_FILE = 'outstanding_requests.txt'

def find_outstanding_request_during_intervals(chrome_network_filename, utilization_filename, output_dir):
    '''
    Finds an outstanding request during each interval
    '''
    interval_utilizations = common_module.parse_utilization_file(utilization_filename)
    requests = common_module.parse_network_file(chrome_network_filename)
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
            line = '{0} {1:f} {2:f} {3:f} {4}'.format((i * interval_size), interval[0], interval[1], utilization, num_outstanding_request)
            output_file.write(line + '\n')


def print_object_duration(requests):
    for request in requests:
        print '{0} {1} {2}'.format(request[0], (request[1][1] - request[1][0]), request)

def print_generic(intervals):
    for interval in intervals:
        print interval

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
