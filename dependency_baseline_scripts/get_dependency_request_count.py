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
            request_count = parse_log(log_filename, page, page_to_run_index[page], num_iterations)
            dependencies = common_module.get_dependencies(dependencies_filename, args.only_important_resources)

            # print times_since_first_request
            if not os.path.exists(args.resource_output_dir):
                os.mkdir(args.resource_output_dir)
            output_resource_count(page, request_count, dependencies, args.resource_output_dir)
        except IndexError as e:
            # print e
            ex_type, ex, tb = sys.exc_info()
            # traceback.print_tb(tb)
            pass
 
def output_resource_count(page, request_count, dependencies, output_dir):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for request in request_count:
            if request in dependencies:
                output_file.write('{0} {1}\n'.format(request, request_count[request]))

def get_page_to_redirected_page_mapping(page_to_redirected_filename):
    with open(page_to_redirected_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { common_module.escape_page(key): common_module.escape_page(value) for key, value in temp }

def parse_log(log_filename, page, index, num_iterations):
    current_request_count = None # Mapping from URL to tuple of (request_timestamp, response_end_timestamp)
    first_request_timestamps, load_intervals = find_load_intervals(log_filename)
    request_count = []
    for i in range(0, len(load_intervals)):
        request_count.append(dict())
        
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
                    port = line[7].split(':')[1]
                    scheme = 'https://' if port == '443' else 'http://'
                    host = line[6]
                    path = line[2]
                    url = scheme + host + path

                    # Get the time to serve this request in microseconds.
                    try:
                        current_request_count = request_count[i]
                        if url not in current_request_count:
                            current_request_count[url] = 0
                        current_request_count[url] += 1
                    except ValueError:
                        pass
                    # Done with this entry.
                    break
    
    first_index_of_last_n_iterations = len(request_count) - num_iterations
    # print page + ' first_index: ' + str(first_index_of_last_n_iterations) + ' len: ' + str(len(first_request_timestamps)) + '; ' + str(len(request_count)) + ' index: ' + str(index)
    request_count = request_count[first_index_of_last_n_iterations:len(request_count)] # Get the last five timings
    # print '{0}'.format(first_request_timestamps[index])
    # print request_count[index]
    return request_count[index]

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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_root_dir')
    parser.add_argument('page_to_run_index')
    parser.add_argument('dependency_directory')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('page_mapping')
    parser.add_argument('resource_output_dir', default=None)
    parser.add_argument('--only-important-resources', default=False, action='store_true')
    args = parser.parse_args()
    main(args.log_root_dir, args.dependency_directory, args.page_to_run_index, args.num_iterations, args.page_mapping)
