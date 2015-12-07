# Graph: CDF across low utilization periods of the number of outstanding requests.
# Low utilization periods are defined in the variable THRESHOLD below.
from argparse import ArgumentParser

import os
import math

THRESHOLD = 0.01

def generate_graph_data(root_dir):
    total_low_utilization_time = 0
    result_dict = dict() # Mapping number of outstanding requests to time that happened.
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            # Skip empty directories
            continue
        
        outstanding_requests_filename = 'outstanding_requests.txt'
        outstanding_requests_full_path = os.path.join(path, outstanding_requests_filename)
        start_end_time_ignoring_bytes_filename = 'start_end_time_ignoring_bytes.txt'
        start_end_time_ignoring_bytes_full_path = os.path.join(path, start_end_time_ignoring_bytes_filename)
        if not os.path.exists(outstanding_requests_full_path) or \
            not os.path.exists(start_end_time_ignoring_bytes_full_path):
            continue
        start_end_time = parse_start_end_time_ignoring_bytes(start_end_time_ignoring_bytes_full_path)
        interval_size = None
        intervals_with_zero_and_one_outstanding_request = []
        with open(outstanding_requests_full_path, 'rb') as input_file:
            line_counter = 0
            for raw_line in input_file:
                line = raw_line.strip().split()
                utilization = float(line[3])
                outstanding_requests = int(line[4])
                
                if interval_size is None:
                    interval_size = int(float(line[2]) - float(line[1]))
                    expected_lines = int(math.ceil(1.0 * (start_end_time[1] - start_end_time[0]) / interval_size))

                if utilization <= THRESHOLD:
                    # Add the number of outstanding requests when the utilization is lower than the threshold.
                    if outstanding_requests not in result_dict:
                        result_dict[outstanding_requests] = 0.0
                    this_interval_size = interval_size
                    if line_counter == expected_lines:
                        this_interval_size = (start_end_time[1] - start_end_time[0]) % interval_size
                    result_dict[outstanding_requests] += this_interval_size
                    total_low_utilization_time += this_interval_size
                    if outstanding_requests <= 1:
                        intervals_with_zero_and_one_outstanding_request.append((line[1], line[2]))
                line_counter += 1
        output_intervals_with_zero_or_one_request(intervals_with_zero_and_one_outstanding_request, path)
    sorted_result_dict = sorted(result_dict.iteritems(), key=lambda x: x[0])
    return sorted_result_dict, total_low_utilization_time

def output_intervals_with_zero_or_one_request(result, path):
    full_path = os.path.join(path, 'intervals_with_zero_or_one.txt')
    with open(full_path, 'wb') as output_file:
        for interval in result:
            output_file.write('{0} {1}\n'.format(interval[0], interval[1]))

def print_results(sorted_result_dict, total_low_utilization_time):
    cumulative_sum = 0.0
    for low_utilization_time in sorted_result_dict:
        cumulative_sum += low_utilization_time[1]
        print '{0} {1}'.format(low_utilization_time[0], (cumulative_sum / total_low_utilization_time))

def parse_start_end_time_ignoring_bytes(filename):
    with open(filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return (float(line[1]), float(line[2]))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    sorted_result_dict, total_low_utilization_time = generate_graph_data(args.root_dir)
    print_results(sorted_result_dict, total_low_utilization_time)
