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
        
        outstanding_requests_filename = 'requests_after_interval.txt'
        outstanding_requests_full_path = os.path.join(path, outstanding_requests_filename)
        if not os.path.exists(outstanding_requests_full_path):
            continue
        interval_size = None
        intervals_with_zero_and_one_outstanding_request = []
        with open(outstanding_requests_full_path, 'rb') as input_file:
            line_counter = 0
            for raw_line in input_file:
                line = raw_line.strip().split()
                outstanding_requests = int(line[3])
                
                if interval_size is None:
                    interval_size = int(float(line[2]) - float(line[1]))

                # Add the number of outstanding requests when the utilization is lower than the threshold.
                if outstanding_requests not in result_dict:
                    result_dict[outstanding_requests] = 0.0
                this_interval_size = interval_size
                result_dict[outstanding_requests] += this_interval_size
                total_low_utilization_time += this_interval_size
                if outstanding_requests <= 1:
                    intervals_with_zero_and_one_outstanding_request.append((line[1], line[2]))
                line_counter += 1
            if line_counter > 0:
                pass
                # print 'Has content.'
    sorted_result_dict = sorted(result_dict.iteritems(), key=lambda x: x[0])
    return sorted_result_dict, total_low_utilization_time

def print_results(sorted_result_dict, total_low_utilization_time):
    cumulative_sum = 0.0
    for low_utilization_time in sorted_result_dict:
        cumulative_sum += low_utilization_time[1]
        print '{0} {1}'.format(low_utilization_time[0], (cumulative_sum / total_low_utilization_time))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    sorted_result_dict, total_low_utilization_time = generate_graph_data(args.root_dir)
    print_results(sorted_result_dict, total_low_utilization_time)
