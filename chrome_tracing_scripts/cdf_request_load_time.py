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
        request_load_times.extend(compute_load_times(request_start_end_time))
    request_load_times.sort()
    for request_load_time in request_load_times:
        print request_load_time
        
def compute_load_times(request_start_end_times):
    result = []
    for request_start_end_time in request_start_end_times:
        result.append(request_start_end_time[1][1] - request_start_end_time[1][0])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    find_request_load_times(args.root_dir)

