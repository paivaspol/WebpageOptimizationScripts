from argparse import ArgumentParser

import http_record_pb2

import common_module
import os
import simplejson as json

def main(root_dir, output_dir, page_list, page_to_time_mapping):
    for page in page_list:
        page = common_module.escape_page(page)
        timestamp = page_to_time_mapping[page]
        page_directory = os.path.join(root_dir, timestamp, page)
        page_output_dir = os.path.join(output_dir, page)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)
        url_to_size_map = get_file_size_for_page(page_directory)
        write_resource_size_map(url_to_size_map, output_dir, page)

def write_resource_size_map(url_to_size_map, output_dir, page):
    output_filename = os.path.join(output_dir, page, 'resource_size.txt')
    with open(output_filename, 'wb') as output_file:
        for url, size in url_to_size_map.iteritems():
            output_file.write('{0} {1}\n'.format(url, size))

def get_file_size_for_page(page_directory):
    url_to_size_map = dict()
    file_list = os.listdir(page_directory)
    for filename in file_list:
        record_filename = os.path.join(page_directory, filename)
        url, content_length = get_content_size(record_filename)
        url_to_size_map[url] = content_length
    return url_to_size_map

def get_content_size(filename):
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line
        splitted_first_line = first_line.split()
        response_object = request_response.response
        url = splitted_first_line[1]
        content_length = -1
        for header_object in request_response.response.header:
            if header_object.key == 'Content-Length':
                content_length = header_object.value
        return url, content_length

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('page_to_time_mapping')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    page_list = common_module.get_page_list(args.page_list)
    page_to_time_mapping = common_module.get_page_to_time_mapping(args.page_to_time_mapping)
    main(args.root_dir, args.output_dir, page_list, page_to_time_mapping)
