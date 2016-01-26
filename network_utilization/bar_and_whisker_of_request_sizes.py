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
                utilizations = float(line[3])
                # if num_requests <= num_objects_threshold and utilizations > utilization_threshold:
                sum_request_sizes = 0
                for i in range(4, len(line)):
                    request_id = line[i]
                    sum_request_sizes += requests_to_sizes[request_id]
                request_sizes_per_interval.append((num_requests, utilizations, sum_request_sizes))
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
    num_requests_to_utilizations = dict()
    for interval_data in request_sizes:
        num_requests, utilization, request_sizes = interval_data
        if num_requests not in num_requests_to_request_sizes:
            num_requests_to_request_sizes[num_requests] = []
            num_requests_to_utilizations[num_requests] = []
        num_requests_to_request_sizes[num_requests].append(request_sizes)
        num_requests_to_utilizations[num_requests].append(utilization)
    result_requests_to_request_size_datapoints = dict()
    result_requests_to_utilizations_datapoints = dict()
    for num_requests in num_requests_to_request_sizes:
        request_size_for_requests = num_requests_to_request_sizes[num_requests]
        utilizations_for_requests = num_requests_to_utilizations[num_requests]
        result_requests_to_request_size_datapoints[num_requests] = generate_find_datapoints(request_size_for_requests)
        result_requests_to_utilizations_datapoints[num_requests] = generate_find_datapoints(utilizations_for_requests)
    output_filename = os.path.join(output_dir, 'median_sum_requests.txt')
    write_to_file(result_requests_to_request_size_datapoints, output_filename)
    output_filename = os.path.join(output_dir, 'median_utilizations.txt')
    write_to_file(result_requests_to_utilizations_datapoints, output_filename)

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
