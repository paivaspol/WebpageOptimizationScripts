from argparse import ArgumentParser

import os

def generate_cdf_of_request_fraction(root_dir):
    result = dict()
    total_time = 0.0
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        request_after_filename = 'requests_after_interval.txt'
        request_after_full_path = os.path.join(path, request_after_filename)
        start_end_time_filename = 'start_end_time_ignoring_bytes.txt'
        start_end_time_full_path = os.path.join(path, start_end_time_filename)
        if os.path.exists(request_after_full_path) and os.path.exists(start_end_time_full_path):
            start_end_time = parse_start_end_time(start_end_time_full_path)
            with open(request_after_full_path, 'rb') as input_file:
                for raw_line in input_file:
                    line = raw_line.strip().split()
                    start_interval = float(line[1])
                    end_interval = float(line[2])
                    requests_after = int(line[3])
                    total_requests = int(line[4])
                    interval_size = min(start_end_time[1], end_interval) - start_interval
                    ratio = 1.0 * requests_after / total_requests
                    if ratio not in result:
                        result[ratio] = 0.0
                    result[ratio] += interval_size
                    total_time += interval_size
    sorted_result = sorted(result.iteritems(), key=lambda x: x[0])
    return sorted_result, total_time

def parse_start_end_time(start_end_time_filename):
    with open(start_end_time_filename, 'rb') as input_file:
        line = input_file.readline().split()
        return (float(line[1]), float(line[2]))

def print_result(result_ratios, total_time):
    cumulative_time = 0.0
    for result_ratio in result_ratios:
        cumulative_time += result_ratio[1]
        print '{0} {1}'.format(result_ratio[0], (1.0 * cumulative_time / total_time))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    result_ratios, total_time = generate_cdf_of_request_fraction(args.root_dir)
    print_result(result_ratios, total_time)
