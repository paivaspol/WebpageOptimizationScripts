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
                utilizations = float(line[4])
                # if num_requests <= num_objects_threshold and utilizations > utilization_threshold:
                sum_request_sizes = 0
                for i in range(5, len(line)):
                    request_id = line[i]
                    sum_request_sizes = max(sum_request_sizes, requests_to_sizes[request_id])
                request_sizes_per_interval.append((num_requests, utilizations, sum_request_sizes))
    return request_sizes_per_interval

def get_request_sizes(request_sizes_filename):
    result = dict()
    with open(request_sizes_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

def write_to_file(results, output_filename):
    sorted_results = sorted([x for x in results if x[0] > 0], key=lambda x: x[2])
    with open(output_filename, 'wb') as output_file:
        for result in sorted_results:
            output_file.write(str(result[2]) + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    request_sizes = find_request_sizes(args.root_dir)
    write_to_file(request_sizes, args.output_dir)
