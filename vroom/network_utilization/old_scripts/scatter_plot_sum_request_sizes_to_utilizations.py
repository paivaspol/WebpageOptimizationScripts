from argparse import ArgumentParser

import common_module
import os

def find_request_sizes_to_utilization(root_dir, pages_to_use):
    request_sizes_per_interval = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        if len(pages_to_use) == 0 or url in pages_to_use:
            interval_request_filename = os.path.join(path, '100ms_interval_num_request.txt')
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
                        sum_request_sizes += requests_to_sizes[request_id]
                    request_sizes_per_interval.append((num_requests, utilizations, sum_request_sizes))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--pages-to-use', default=None)
    args = parser.parse_args()
    pages_to_use = common_module.parse_pages_to_use(args.pages_to_use)

