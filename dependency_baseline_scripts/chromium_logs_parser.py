from argparse import ArgumentParser
from collections import defaultdict

import os
import numpy

def main(root_dir, dependency_dir, num_iterations):
    dependency_discovery_times = defaultdict(list)
    for i in range(0, num_iterations):
        pages = os.listdir(os.path.join(root_dir, str(i)))
        for page in pages:
            chromium_log_filename = os.path.join(root_dir, str(i), page, 'chromium_log.txt')
            start_end_time_filename = os.path.join(root_dir, str(i), page, 'start_end_time_' + page)
            dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
            if not (os.path.exists(chromium_log_filename) and \
                    os.path.exists(start_end_time_filename) and \
                    os.path.exists(dependency_filename)):
                continue
            dependency_set = populate_dependencies(dependency_filename)
            start_time, _ = get_start_end_time(start_end_time_filename) if not args.use_first_request_timestamp else (None, None)
            start_time, latest_timestamp = parse_chromium_log(chromium_log_filename, dependency_set, start_time)
            difference = (latest_timestamp - start_time)
            load_info = (start_time, latest_timestamp, difference)
            dependency_discovery_times[page].append(load_info)
    median_discovery_time_result = find_median(dependency_discovery_times)
    for page, median_discovery_time in median_discovery_time_result.iteritems():
        print '{0} {1} {2} {3}'.format(page, median_discovery_time[0], \
                                       median_discovery_time[1], \
                                       median_discovery_time[2])

def find_median(dependency_discovery_times_dict):
    result = dict()
    for page, dependency_discovery_times in dependency_discovery_times_dict.iteritems():
        differences = [ x for _, _, x in dependency_discovery_times if x > 0 ]
        if len(differences) > 0:
            median = numpy.median(differences)
            for discovery_time in dependency_discovery_times:
                if median == discovery_time[2]:
                    result[page] = discovery_time
    return result

def populate_dependencies(dependency_filename):
    dependency_set = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            dependency_set.add(line[2])
    return dependency_set

def get_start_end_time(start_end_time_filename):
    with open(start_end_time_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return int(line[1]), int(line[2])

def parse_chromium_log(chromium_log_filename, dependency_set, start_time):
    latest_timestamp = -1
    with open(chromium_log_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            timestamp = '2016-' + line[0] + ' ' + line[1]
            if start_time is None and 'Starting Asynchronous' in raw_line:
                start_time = int(line[len(line) - 1])
            elif 'Submitting Dependency Request' in raw_line:
                url = line[len(line) - 1]
                timestamp = int(line[len(line) - 2])
                if url in dependency_set:
                    dependency_set.remove(url)
                    latest_timestamp = max(latest_timestamp, timestamp)
    return start_time, latest_timestamp

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('--use-first-request-timestamp', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir, args.num_iterations)
