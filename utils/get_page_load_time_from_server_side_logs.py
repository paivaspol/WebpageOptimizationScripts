from argparse import ArgumentParser 
from datetime import datetime

import common_module
import os

def main(root_dir, page_to_run_index_filename, num_iterations, page_to_redirected, page_list):
    pages = os.listdir(root_dir)
    page_to_redirected_url = get_page_to_redirected_page_mapping(page_to_redirected)
    page_to_run_index = get_page_to_run_index(page_to_run_index_filename)
    pages_to_use = None
    if page_list is not None:
        pages_to_use = get_page_list(page_list)
        
    for page in pages:
        log_filename = os.path.join(root_dir, page)
        if page not in page_to_run_index or \
            not os.path.exists(log_filename):
            page = page_to_redirected_url[page]
            if page not in page_to_run_index or \
                not os.path.exists(log_filename):
                # print 'dependency filename: ' + dependencies_filename
                # print 'error: ' + page + ' page_in_dict: ' + str(page in page_to_run_index) + ' exists: ' + str(os.path.exists(dependencies_filename))
                continue
        if pages_to_use is not None and page not in pages_to_use:
            continue
        try:
            first_request_timestamp, timings = parse_log(log_filename, page, page_to_run_index[page], num_iterations)
            times_since_first_request = get_times_since_first_request(first_request_timestamp, timings)
            if len(times_since_first_request) > 0:
                print '{0} {1}'.format(page, max(times_since_first_request.values()))
        except IndexError as e:
            pass

def get_page_list(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        return [ line.strip() for line in input_file ]

def get_page_to_redirected_page_mapping(page_to_redirected_filename):
    with open(page_to_redirected_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { common_module.escape_page(key): common_module.escape_page(value) for key, value in temp }

def get_times_since_first_request(first_request_timestamp, timings):
    result = dict()
    for url in timings:
        finish_time = int(timings[url][1])
        load_time = (finish_time - first_request_timestamp) / 1000.0 # Convert from microseconds to ms
        result[url] = load_time
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
                    # print line
                    # Construct full path of the request.
                    port = line[7].split(':')[1]
                    scheme = 'https://' if port == '443' else 'http://'
                    host = line[6]
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
    # print page + ' first_index: ' + str(first_index_of_last_n_iterations) + ' len: ' + str(len(first_request_timestamps)) + '; ' + str(len(timings))
    timings = timings[first_index_of_last_n_iterations:len(timings)] # Get the last five timings
    first_request_timestamps = first_request_timestamps[first_index_of_last_n_iterations:len(first_request_timestamps)]
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
            path = line[2]

            if path == '/':
                # This is a index request. This timestamp must be a beginning of a start request.
                start_intervals.append(timestamp)

    # Construct the load intervals
    load_intervals = []
    for i in range(0, len(start_intervals) - 1):
        load_intervals.append( (start_intervals[i], start_intervals[i + 1]) )
    load_intervals.append( (start_intervals[len(start_intervals) - 1], -1) )
    return start_intervals, load_intervals

def get_page_to_run_index(page_to_run_index):
    with open(page_to_run_index, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: int(value) for key, value in temp }

def get_dependencies(dependency_filename):
    with open(dependency_filename, 'rb') as input_file:
        return [ line.strip().split()[2] for line in input_file if line.strip().split()[4] != 'Document' ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_root_dir')
    parser.add_argument('page_to_run_index')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('page_mapping')
    parser.add_argument('--page-list', default=None)
    args = parser.parse_args()
    main(args.log_root_dir, args.page_to_run_index, args.num_iterations, args.page_mapping, args.page_list)
