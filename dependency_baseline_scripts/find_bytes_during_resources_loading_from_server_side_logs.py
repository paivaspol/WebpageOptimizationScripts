from argparse import ArgumentParser
from urlparse import urlparse

import os

def main(url_root_dir, end_time_mapping, resource_sizes_dir):
    pages = os.listdir(url_root_dir)
    for page in pages:
        # if 'fortune.com' not in page:
        #     continue
        resource_sizes_filename = os.path.join(resource_sizes_dir, page)
        fetch_time_filename = os.path.join(url_root_dir, page)
        if not os.path.exists(resource_sizes_filename) or \
            not os.path.exists(fetch_time_filename) or \
            page not in end_time_mapping:
            continue
        end_time = end_time_mapping[page]
        resource_sizes = get_resource_sizes(resource_sizes_filename)
        unimportant, important, total = find_bytes(fetch_time_filename, end_time, resource_sizes)
        fraction = 1.0 * unimportant / total
        print '{0} {1}'.format(page, fraction)

def find_bytes(fetch_time_filename, end_time, resource_sizes):
    unimportant = 0
    important = 0
    total = 0
    with open(fetch_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            time_since_first_request = float(line[2])
            if time_since_first_request <= end_time and \
                url in resource_sizes:
                parsed_url = urlparse(url)
                # print parsed_url
                if parsed_url.path.endswith('.js') or \
                    parsed_url.path.endswith('.css') or \
                    parsed_url.path.endswith('.html') or \
                    parsed_url.path.endswith('/'):
                    important += resource_sizes[url]
                    # print '[imp] ' + url + ' ' + str(resource_sizes[url])
                else:
                    unimportant += resource_sizes[url]
                    # print '[unimp] ' + url + ' ' + str(resource_sizes[url])
                total += resource_sizes[url]
    return unimportant, important, total

def get_resource_sizes(resource_sizes_filename):
    result = dict()
    with open(resource_sizes_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[2]] = int(line[1])
    return result

def get_end_time_mapping(end_time_mapping_filename):
    result = dict()
    with open(end_time_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = float(line[1])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('url_root_dir')
    parser.add_argument('end_time_mapping')
    parser.add_argument('resource_sizes_dir')
    args = parser.parse_args()
    end_time_mapping = get_end_time_mapping(args.end_time_mapping)
    main(args.url_root_dir, end_time_mapping, args.resource_sizes_dir)
