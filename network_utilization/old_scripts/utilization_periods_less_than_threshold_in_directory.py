from argparse import ArgumentParser

import common_module
import subprocess
import os

def find_utilizations(root_dir, interval_size):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        pcap_filename = os.path.join(path, 'output.pcap')
        network_filename = os.path.join(path, 'network_' + url)
        page_start_end_filename = os.path.join(path, 'start_end_time_' + url)
        requests_to_ignore_filename = os.path.join(path, 'requests_to_ignore.txt')
        command = 'python utilization_periods_less_than_threshold.py {0} {1} {2} --output-dir {3} --interval-size {4} --requests-to-ignore {5}'.format(network_filename, page_start_end_filename, pcap_filename, path, interval_size, requests_to_ignore_filename)
        subprocess.call(command, shell=True)

def aggregate_utilizations(root_dir, interval_size):
    aggregated_utilizations = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        result_filename = os.path.join(path, '{0}ms_interval_num_request.txt'.format(interval_size))
        with open(result_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                aggregated_utilizations.append((int(line[2]), float(line[4])))
    return aggregated_utilizations

def output_to_file(aggregated_utilizations, threshold, output_dir):
    lower_or_eq_threshold = sorted([utilization for requests, utilization in aggregated_utilizations if requests <= threshold and utilization <= 1.0])
    greater_than_threshold = sorted([utilization for requests, utilization in aggregated_utilizations if requests > threshold and utilization <= 1.0])
    print len(lower_or_eq_threshold)
    print len(greater_than_threshold)
    lower_eq_filename = os.path.join(output_dir, 'lower_eq.txt')
    with open(lower_eq_filename, 'wb') as output_file:
        for utilization in lower_or_eq_threshold:
            output_file.write(str(utilization) + '\n')
    greater_filename = os.path.join(output_dir, 'greater.txt')
    with open(greater_filename, 'wb') as output_file:
        for utilization in greater_than_threshold:
            output_file.write(str(utilization) + '\n')

    num_requests = sorted([requests for requests, _ in aggregated_utilizations])
    num_requests_filename = os.path.join(output_dir, 'num_requests.txt')
    with open(num_requests_filename, 'wb') as output_file:
        for num_request in num_requests:
            output_file.write(str(num_request) + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('threshold', type=int)
    parser.add_argument('--dont-compute-utilizations', default=False, action='store_true')
    parser.add_argument('--interval-size', default=100, type=int)
    args = parser.parse_args()
    if not args.dont_compute_utilizations:
        find_utilizations(args.root_dir, args.interval_size)
    aggregated_utilizations = aggregate_utilizations(args.root_dir, args.interval_size)
    output_to_file(aggregated_utilizations, args.threshold, args.output_dir)
