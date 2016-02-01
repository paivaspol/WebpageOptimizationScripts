from argparse import ArgumentParser

import common_module
import os

def find_request_load_times(root_dir):
    request_load_times = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path) 
        full_path = os.path.join(path, 'network_' + url)
        request_start_end_time = common_module.parse_network_file(full_path)
        load_times, requests_with_very_low_load_time = compute_load_times(request_start_end_time)
        request_load_times.extend(load_times)
        output_full_path = os.path.join(path, 'requests_to_ignore.txt')
        write_low_load_time_requests(output_full_path, requests_with_very_low_load_time)
    request_load_times.sort()
    for request_load_time in request_load_times:
        print request_load_time
        
def compute_load_times(request_start_end_times):
    requests_with_very_low_load_time = []
    result = []
    for request_start_end_time in request_start_end_times:
        request_load_time = request_start_end_time[1][1] - request_start_end_time[1][0]
        if request_load_time < 137.00:
            requests_with_very_low_load_time.append(request_start_end_time[0])
        result.append(request_load_time)
    return result, requests_with_very_low_load_time

def write_low_load_time_requests(output_filename, requests):
    with open(output_filename, 'wb') as output_file:
        for request in requests:
            output_file.write('{0}\n'.format(request))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    find_request_load_times(args.root_dir)

