from argparse import ArgumentParser 
from datetime import datetime

import common_module
import os
import sys
import traceback

def main(root_dir, dependency_dir, page_to_run_index_filename, num_iterations, page_to_redirected):
    pages = os.listdir(root_dir)
    page_to_redirected_url = get_page_to_redirected_page_mapping(page_to_redirected)
    page_to_run_index = common_module.get_page_to_run_index(page_to_run_index_filename)
    # print pages
    # print page_to_run_index
    # print page_to_redirected_url
    for page in pages:
        # if not 'news.google.com' in page:
        #     continue
        dependencies_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')

        log_filename = os.path.join(root_dir, page)
        # print '{0} {1} {2}'.format(page, os.path.exists(dependencies_filename), os.path.exists(log_filename))
        if (not os.path.exists(dependencies_filename) or \
                page not in page_to_run_index or \
                not os.path.exists(log_filename)):
            if page in page_to_redirected_url:
                page = page_to_redirected_url[page]
                dependencies_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')

                if not os.path.exists(dependencies_filename) or \
                    page not in page_to_run_index or \
                    not os.path.exists(log_filename):
                    # print 'dependency filename: ' + dependencies_filename
                    # print 'error: ' + page + ' page_in_dict: ' + str(page in page_to_run_index) + ' exists: ' + str(os.path.exists(dependencies_filename))
                    continue
            else:
                continue
        try:
            first_request_timestamp, timings = parse_log(log_filename, page, page_to_run_index[page], num_iterations)
            dependencies = common_module.get_dependencies(dependencies_filename, args.only_important_resources)
            # dependencies = common_module.get_dependencies_without_other_iframes(dependencies_filename, \
            #                                                                 args.only_important_resources, \
            #                                                                 page)

            times_since_first_request = get_times_since_first_request(first_request_timestamp, timings, dependencies)
            # print times_since_first_request
            if len(times_since_first_request) > 0:
                print '{0} {1}'.format(page, max(times_since_first_request.values()))
            if args.resource_output_dir is not None:
                if not os.path.exists(args.resource_output_dir):
                    os.mkdir(args.resource_output_dir)
                output_resource_fetch_time(page, timings, times_since_first_request, dependencies, args.resource_output_dir)
        except IndexError as e:
            # print e
            ex_type, ex, tb = sys.exc_info()
            # traceback.print_tb(tb)
            pass
 
def output_resource_fetch_time(page, request_times, times_since_first_request, dependencies, output_dir):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        sorted_times_since_first_request = sorted(times_since_first_request.iteritems(), key=lambda x: x[1])
        for i in range(0, len(sorted_times_since_first_request)):
            dependency, time_since_first_request = sorted_times_since_first_request[i]
            request_time = request_times[dependency][0]
            if dependency in dependencies:
                output_file.write('{0} {1} {2}\n'.format(dependency, request_time, time_since_first_request))

def get_page_to_redirected_page_mapping(page_to_redirected_filename):
    with open(page_to_redirected_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { common_module.escape_page(key): common_module.escape_page(value) for key, value in temp }

def get_times_since_first_request(first_request_timestamp, timings, dependencies):
    result = dict()
    for dependency in dependencies:
        if dependency in timings:
            finish_time = int(timings[dependency][1])
            load_time = (finish_time - first_request_timestamp) / 1000.0 # Convert from microseconds to ms
            load_time = load_time / 1000.0 # Convert from ms to s
            result[dependency] = load_time
            # print '{0} {1}'.format(dependency, load_time)
    return result

def parse_log(log_filename, page, index, num_iterations):
    current_timings = None # Mapping from URL to tuple of (request_timestamp, response_end_timestamp)
    first_request_timestamps, load_intervals = find_load_intervals(log_filename)
    timings = []
    for i in range(0, len(load_intervals)):
        timings.append(dict())
        
    with open(log_filename, 'rb') as input_file:
        for raw_line in input_file:
            if raw_line.startswith('['):
                continue

            line = raw_line.strip().split(' ')

            # Get timestamp.
            timestamp = int(line[0]) # microsecond precision
            
            # Find the load index
            for i in range(0, len(load_intervals)):
                interval = load_intervals[i]
                if interval[0] <= timestamp < interval[1] or \
                    (interval[0] <= timestamp and interval[1] == -1):
                    # Construct full path of the request.
                    #print line
                    if len(line) == 8:
                        # Old log format
                        port = line[len(line) - 1].split(':')[1]
                        scheme = 'https://' if port == '443' else 'http://'
                        host = line[len(line) - 2]
                        path = line[2]
                        url = scheme + host + path
                        escaped_url = common_module.escape_page(url)
                    else: 
                        port = line[len(line) - 2].split(':')[1]
                        scheme = 'https://' if port == '443' else 'http://'
                        host = line[len(line) - 3]
                        path = line[2]
                        url = scheme + host + path
                        escaped_url = common_module.escape_page(url)

                    # Get the time to serve this request in microseconds.
                    try:
                        time_to_serve = int(line[4])
                        completion_time = timestamp + time_to_serve
                        current_timings = timings[i]
                        if url not in current_timings:
                            current_timings[url] = (timestamp, completion_time)
                    except ValueError:
                        pass
                    # Done with this entry.
                    break
    
    first_index_of_last_n_iterations = len(timings) - num_iterations
    # print page + ' first_index: ' + str(first_index_of_last_n_iterations) + ' len: ' + str(len(first_request_timestamps)) + '; ' + str(len(timings)) + ' index: ' + str(index)
    timings = timings[first_index_of_last_n_iterations:len(timings)] # Get the last five timings
    first_request_timestamps = first_request_timestamps[first_index_of_last_n_iterations:len(first_request_timestamps)]
    # print '{0}'.format(first_request_timestamps[index])
    # print timings[index]
    return first_request_timestamps[index], timings[index]

def find_load_intervals(server_side_log_filename):
    start_intervals = []
    with open(server_side_log_filename, 'rb') as input_file:
        for raw_line in input_file:
            if raw_line.startswith('['):
                continue

            line = raw_line.strip().split(' ')

            # Get timestamp.
            timestamp = int(line[0]) # microsecond precision
            method = line[1]
            path = line[2]

            if method == 'GET' and path == '/':
                # This is a index request. This timestamp must be a beginning of a start request.
                start_intervals.append(timestamp)

    # Construct the load intervals
    load_intervals = []
    for i in range(0, len(start_intervals) - 1):
        load_intervals.append( (start_intervals[i], start_intervals[i + 1]) )
    load_intervals.append( (start_intervals[len(start_intervals) - 1], -1) )
    return start_intervals, load_intervals

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_root_dir')
    parser.add_argument('page_to_run_index')
    parser.add_argument('dependency_directory')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('page_mapping')
    parser.add_argument('--resource-output-dir', default=None)
    parser.add_argument('--only-important-resources', default=False, action='store_true')
    args = parser.parse_args()
    main(args.log_root_dir, args.dependency_directory, args.page_to_run_index, args.num_iterations, args.page_mapping)
