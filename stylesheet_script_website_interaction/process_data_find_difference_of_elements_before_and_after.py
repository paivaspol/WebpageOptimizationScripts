from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os

def process_files(root_dir):
    for directory in os.listdir(root_dir):
        summary_filename = os.path.join(root_dir, directory, 'summary.txt')
        request_id_to_url_filename = os.path.join(root_dir, directory, 'request_id_to_url.txt')
        if not os.path.exists(summary_filename) or not os.path.exists(request_id_to_url_filename):
            continue
        request_id_to_url_dict = get_request_id_to_url_dict(request_id_to_url_filename)
        summary_dict = get_summary_dict(summary_filename, request_id_to_url_dict, directory)
        before_elements = sum([ x for x, _ in summary_dict.values() ])
        after_elements = sum([ y for _, y in summary_dict.values() ])
        difference = after_elements - before_elements
        print '{0} {1} {2} {3}'.format(directory, before_elements, after_elements, difference)

def get_request_id_to_url_dict(request_id_to_url_filename):
    result_dict = dict()
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result_dict[line[0]] = line[1]
    return result_dict

def get_summary_dict(summary_filename, request_id_to_url, page_domain):
    result = dict()
    with open(summary_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            request_id = line[0][:len(line[0]) - len('.beautified')]
            if page_domain != common_module.extract_domain(request_id_to_url[request_id]):
                result[line[0]] = (int(line[1]), int(line[2]))
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    process_files(args.root_dir)
