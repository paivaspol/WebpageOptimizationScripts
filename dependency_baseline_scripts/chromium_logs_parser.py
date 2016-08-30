from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime

import os
import numpy

def main(root_dir, dependency_dir, num_iterations):
    dependency_discovery_times = defaultdict(list)
    start_iteration = 0
    end_iteration = num_iterations
    if args.skip_first_load:
        start_iteration += 1
        end_iteration += 1
    for i in range(start_iteration, end_iteration):
        pages = os.listdir(os.path.join(root_dir, str(i)))
        for page in pages:
            # print 'processing: ' + page
            chromium_log_filename = os.path.join(root_dir, str(i), page, 'chromium_log.txt')
            start_end_time_filename = os.path.join(root_dir, str(i), page, 'start_end_time_' + page)
            dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
            if not (os.path.exists(chromium_log_filename) and \
                    os.path.exists(dependency_filename)):
                print chromium_log_filename
                print 'here'
                continue
            dependency_set = populate_dependencies(dependency_filename)
            start_time, _ = get_start_end_time(start_end_time_filename) if not args.use_first_request_timestamp else (None, None)
            start_time, latest_timestamp = parse_chromium_log(chromium_log_filename, dependency_set, start_time)
            # print 'start_time: {0}, latest_timestamp: {1}'.format(start_time, latest_timestamp)
            if start_time is not None and latest_timestamp > 0:
                difference = (latest_timestamp - start_time)
                load_info = (start_time, latest_timestamp, difference)
                dependency_discovery_times[page].append(load_info)
    median_discovery_time_result = find_median(dependency_discovery_times, num_iterations)
    if not args.display_failed_websites:
        for page, median_discovery_time in median_discovery_time_result.iteritems():
            print '{0} {1:.0f} {2:.0f} {3:.0f} {4}'.format(page, median_discovery_time[0][0], \
                                           median_discovery_time[0][1], \
                                           median_discovery_time[0][2],
                                           median_discovery_time[1])

def find_median(dependency_discovery_times_dict, num_iterations):
    result = dict()
    for page, dependency_discovery_times in dependency_discovery_times_dict.iteritems():
        if args.output_raw_data:
            print '{0} {1}'.format(page, dependency_discovery_times)
        differences = [ x for _, _, x in dependency_discovery_times if x > 0 ]
        if len(differences) == num_iterations:
            median = numpy.median(differences)
            for i in range(0, num_iterations):
                discovery_time = dependency_discovery_times[i]
                if median == discovery_time[2]:
                    result[page] = (discovery_time, i)
        elif args.display_failed_websites and len(differences) != num_iterations:
            print page
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
            timestamp_str = '2016-' + line[0] + ' ' + line[1]
            if start_time is None and 'Starting Asynchronous' in raw_line:
                datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                epoch = datetime.utcfromtimestamp(0)
                millis_since_epoch = (datetime_obj - epoch).total_seconds() * 1000.0
                start_time = millis_since_epoch
            elif 'Submitting Dependency Request' in raw_line:
                url = line[len(line) - 1]
                datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                epoch = datetime.utcfromtimestamp(0)
                millis_since_epoch = (datetime_obj - epoch).total_seconds() * 1000.0
                timestamp = millis_since_epoch
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
    parser.add_argument('--output-raw-data', default=False, action='store_true')
    parser.add_argument('--skip-first-load', default=False, action='store_true')
    parser.add_argument('--display-failed-websites', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir, args.num_iterations)
