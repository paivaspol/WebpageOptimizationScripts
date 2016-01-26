from argparse import ArgumentParser

import os

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

def output_to_file(result, output_dir, utilization_threshold, num_objects_threshold):
    object_size_during_utilization_over_threshold_and_below_num_objects = sorted([sum_outstanding_request_sizes for num_requests, utilizations, sum_outstanding_request_sizes in result if utilizations > utilization_threshold and num_requests <= num_objects_threshold])
    object_size_during_utilization_below_threshold_and_below_num_objects = sorted([sum_outstanding_request_sizes for num_requests, utilizations, sum_outstanding_request_sizes in result if utilizations <= utilization_threshold and num_requests <= num_objects_threshold])
    output_full_path = os.path.join(output_dir, 'object_size_during_utilization_over_threshold_and_below_num_objects.txt')
    write_to_file(object_size_during_utilization_over_threshold_and_below_num_objects, output_full_path)
    output_full_path = os.path.join(output_dir, 'object_size_during_utilization_below_threshold_and_below_num_objects.txt')
    write_to_file(object_size_during_utilization_below_threshold_and_below_num_objects, output_full_path)

    object_size_during_utilization_over_threshold_and_below_num_objects = sorted([sum_outstanding_request_sizes for num_requests, utilizations, sum_outstanding_request_sizes in result if utilizations > utilization_threshold and num_requests > num_objects_threshold])
    object_size_during_utilization_below_threshold_and_below_num_objects = sorted([sum_outstanding_request_sizes for num_requests, utilizations, sum_outstanding_request_sizes in result if utilizations <= utilization_threshold and num_requests > num_objects_threshold])
    output_full_path = os.path.join(output_dir, 'object_size_during_utilization_over_threshold_and_above_num_objects.txt')
    write_to_file(object_size_during_utilization_over_threshold_and_below_num_objects, output_full_path)
    output_full_path = os.path.join(output_dir, 'object_size_during_utilization_below_threshold_and_above_num_objects.txt')
    write_to_file(object_size_during_utilization_below_threshold_and_below_num_objects, output_full_path)

def write_to_file(result_list, output_filename):
    with open(output_filename, 'wb') as output_file:
        for request_size in result_list:
            output_file.write(str(request_size) + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('utilization_threshold', type=float)
    parser.add_argument('num_objects_threshold', type=int)
    parser.add_argument('output_dir')
    args = parser.parse_args()
    request_sizes = find_request_sizes(args.root_dir)
    output_to_file(request_sizes, args.output_dir, args.utilization_threshold, args.num_objects_threshold)
