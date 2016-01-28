from argparse import ArgumentParser

import os
import numpy

def find_request_sizes(root_dir):
    request_sizes_per_interval = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        interval_request_filename = os.path.join(path, '100ms_interval_num_request.txt')
        requests_to_sizes_filename = os.path.join(path, 'request_sizes.txt')
        requests_to_sizes = get_request_sizes(requests_to_sizes_filename)
        with open(interval_request_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                num_requests = int(line[2])
                actual_bytes_downloaded = int(line[3])
                request_sizes_per_interval.append((num_requests, actual_bytes_downloaded))
    return request_sizes_per_interval

def get_request_sizes(request_sizes_filename):
    result = dict()
    with open(request_sizes_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

def generate_bar_and_whisker(request_sizes, output_dir):
    num_requests_to_request_sizes = dict()
    for interval_data in request_sizes:
        num_requests, actual_bytes_downloaded = interval_data
        if num_requests not in num_requests_to_request_sizes:
            num_requests_to_request_sizes[num_requests] = []
        num_requests_to_request_sizes[num_requests].append(actual_bytes_downloaded)
    result_requests_to_request_size_datapoints = dict()
    for num_requests in num_requests_to_request_sizes:
        request_size_for_requests = num_requests_to_request_sizes[num_requests]
        result_requests_to_request_size_datapoints[num_requests] = generate_find_datapoints(request_size_for_requests)
    output_filename = os.path.join(output_dir, 'median_actual_bytes_downloaded.txt')
    write_to_file(result_requests_to_request_size_datapoints, output_filename)

def generate_find_datapoints(data_list):
    return numpy.median(data_list)
    # result = []
    # percentiles = [10, 25, 50, 75, 90]
    # for percentile in percentiles:
    # return result

def write_to_file(results, output_filename):
    with open(output_filename, 'wb') as output_file:
        for result in results:
            output_file.write(str(result) + ' ' + str(results[result]) + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    request_sizes = find_request_sizes(args.root_dir)
    generate_bar_and_whisker(request_sizes, args.output_dir)
