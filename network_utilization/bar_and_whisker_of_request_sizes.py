from argparse import ArgumentParser

import common_module
import os
import numpy

def find_request_sizes(root_dir, pages_to_use, interval_size, requests_to_ignore):
    request_sizes_per_interval = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        current_url_requests_to_ignore = requests_to_ignore[url]
        if len(pages_to_use) == 0 or url in pages_to_use:
            interval_request_filename = os.path.join(path, '{0}ms_interval_num_request.txt'.format(interval_size))
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
                        if request_id not in current_url_requests_to_ignore:
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
    request_sizes_to_utilizations = dict()
    for interval_data in request_sizes:
        num_requests, utilization, request_size = interval_data
        # Num request to * mapping
        if num_requests not in num_requests_to_request_sizes:
            num_requests_to_request_sizes[num_requests] = []
            num_requests_to_utilizations[num_requests] = []
        num_requests_to_request_sizes[num_requests].append(request_size)
        num_requests_to_utilizations[num_requests].append(utilization)

        # Request size to utilization dictionary.
        rounded_request_size = round_to_closest(request_size)
        if rounded_request_size not in request_sizes_to_utilizations:
            request_sizes_to_utilizations[rounded_request_size] = []
        request_sizes_to_utilizations[rounded_request_size].append(utilization)
    # Num request to * mapping.
    result_requests_to_request_size_datapoints = dict()
    result_requests_to_utilizations_datapoints = dict()
    for num_requests in num_requests_to_request_sizes:
        request_size_for_requests = num_requests_to_request_sizes[num_requests]
        utilizations_for_requests = num_requests_to_utilizations[num_requests]
        if len(request_size_for_requests) >= 5:
            result_requests_to_request_size_datapoints[num_requests] = generate_find_datapoints(request_size_for_requests)
            result_requests_to_utilizations_datapoints[num_requests] = generate_find_datapoints(utilizations_for_requests)
        print 'num_requests: ' + str(num_requests) + ' request_size: ' + str(len(request_size_for_requests)) + ' request_to_utilization: ' + str(len(utilizations_for_requests))
    # Request size to utilization mapping.
    result_request_sizes_to_utilization_datapoints = dict()
    for request_size in request_sizes_to_utilizations:
        print 'request_size: {0} len(utilizations): {1}'.format(request_size, len(request_sizes_to_utilizations[request_size]))
        result_request_sizes_to_utilization_datapoints[request_size] = generate_find_datapoints(request_sizes_to_utilizations[request_size])
        
    output_filename = os.path.join(output_dir, 'num_requests_to_sum_requests.txt')
    write_to_file(result_requests_to_request_size_datapoints, output_filename)
    output_filename = os.path.join(output_dir, 'num_requests_to_utilizations.txt')
    write_to_file(result_requests_to_utilizations_datapoints, output_filename)
    output_filename = os.path.join(output_dir, 'request_sizes_to_utilizations.txt')
    write_to_file(result_request_sizes_to_utilization_datapoints, output_filename)

def round_to_closest(data, closest=2000.0):
    return round(data / closest) * closest

def generate_find_datapoints(data_list):
    return numpy.average(data_list)
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
    parser.add_argument('--pages-to-use', default=None)
    parser.add_argument('--requests-to-ignore', default=None)
    parser.add_argument('--interval-size', default=100, type=int)
    args = parser.parse_args()
    pages_to_use = common_module.parse_pages_to_use(args.pages_to_use)
    requests_to_ignore = common_module.parse_requests_to_ignore(args.requests_to_ignore)
    request_sizes = find_request_sizes(args.root_dir, pages_to_use, args.interval_size, requests_to_ignore)
    generate_bar_and_whisker(request_sizes, args.output_dir)
