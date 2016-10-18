from argparse import ArgumentParser 
from datetime import datetime

import common_module
import os

def main(root_dir, dependency_dir, page_to_run_index_filename, num_iterations, page_to_redirected, target_page):
    pages = os.listdir(root_dir)
    page_to_redirected_url = get_page_to_redirected_page_mapping(page_to_redirected)
    page_to_run_index = get_page_to_run_index(page_to_run_index_filename)
    for page in pages:
        if page != common_module.escape_page(target_page):
            continue
        dependencies_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        log_filename = os.path.join(root_dir, page)
        if not os.path.exists(dependencies_filename) or \
                page not in page_to_run_index or \
                not os.path.exists(log_filename):
            page = page_to_redirected_url[page]
            dependencies_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
            if not os.path.exists(dependencies_filename) or \
                page not in page_to_run_index or \
                not os.path.exists(log_filename):
                # print 'dependency filename: ' + dependencies_filename
                # print 'error: ' + page + ' page_in_dict: ' + str(page in page_to_run_index) + ' exists: ' + str(os.path.exists(dependencies_filename))
                continue
        try:
            first_request_timestamp, timings = parse_log(log_filename, page, page_to_run_index[page], num_iterations)
            dependencies = get_dependencies(dependencies_filename)
            print dependencies
            times_since_first_request = get_times_since_first_request(first_request_timestamp, timings, dependencies)
            if len(times_since_first_request) > 0:
                print page
                sorted_times_since_first_request = sorted(times_since_first_request.iteritems(), key=lambda x: x[1])
                for url, time in sorted_times_since_first_request:
                    print '\t{0} {1} {2} {3}'.format(url, time, first_request_timestamp, timings[url])
        except IndexError as e:
            pass

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
            result[dependency] = load_time
            # print '{0} {1}'.format(dependency, load_time)
    return result

def parse_log(log_filename, page, index, num_iterations):
    current_timings = None # Mapping from URL to tuple of (request_timestamp, response_end_timestamp)
    timings = []
    first_request_timestamps = []
    with open(log_filename, 'rb') as input_file:
        for raw_line in input_file:
            if raw_line.startswith('['):
                continue

            line = raw_line.strip().split(' ')

            # Get timestamp.
            timestamp = int(line[0]) # microsecond precision

            # Construct full path of the request.
            port = line[len(line) - 1].split(':')[1]
            scheme = 'https://' if port == '443' else 'http://'
            host = line[len(line) - 2]
            path = line[2]
            url = scheme + host + path
            escaped_url = common_module.escape_page(url)
            if escaped_url == page:
                # We found a new replay. Create a new entry for this replay.
                current_timings = dict()
                timings.append(current_timings)
                first_request_timestamps.append(timestamp)
            
            if current_timings is None:
                # Don't do anything when the current timings is None
                continue

            # Get the time to serve this request in microseconds.
            time_to_serve = int(line[4])
            completion_time = timestamp + time_to_serve
            if url not in current_timings:
                current_timings[url] = (timestamp, completion_time)
    
    first_index_of_last_n_iterations = len(timings) - num_iterations
    # print page + ' first_index: ' + str(first_index_of_last_n_iterations) + ' len: ' + str(len(first_request_timestamps)) + '; ' + str(len(timings))
    timings = timings[first_index_of_last_n_iterations:len(timings)] # Get the last five timings
    first_request_timestamps = first_request_timestamps[first_index_of_last_n_iterations:len(first_request_timestamps)]
    return first_request_timestamps[index], timings[index]

def get_page_to_run_index(page_to_run_index):
    with open(page_to_run_index, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: int(value) for key, value in temp }

def get_dependencies(dependency_filename):
    with open(dependency_filename, 'rb') as input_file:
        return [ line.strip().split()[2] for line in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_root_dir')
    parser.add_argument('page_to_run_index')
    parser.add_argument('dependency_directory')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('page_mapping')
    parser.add_argument('target_page')
    args = parser.parse_args()
    main(args.log_root_dir, args.dependency_directory, args.page_to_run_index, args.num_iterations, args.page_mapping, args.target_page)
