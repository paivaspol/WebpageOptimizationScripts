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
        file_list = os.listdir(page_directory)
        page_output_dir = os.path.join(output_dir, page)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)

        record_to_url_mapping = os.path.join(page_output_dir, 'record_filename_to_url.txt')
        requests = dict()
        requests['requests'] = []
        with open(record_to_url_mapping, 'wb') as output_file:
            for filename in file_list:
                record_filename = os.path.join(page_directory, filename)
                request_object = generate_request_object_for_file(record_filename)
                request_object['record_filename'] = filename
                mapping = '{0} {1}\n'.format(request_object['url'], filename)
                output_file.write(mapping)
                requests['requests'].append(request_object)

        requests_output_path = os.path.join(output_dir, page, 'requests.json')
        with open(requests_output_path, 'wb') as output_file:
            output_file.write(json.dumps(requests))

def generate_request_object_for_file(filename):
    request_object = dict()
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line
        splitted_first_line = first_line.split()
        request_object['type'] = splitted_first_line[0]
        request_object['url'] = splitted_first_line[1]
        request_object['first_line'] = request_response.request.first_line
        request_object['headers'] = dict()
        for header_object in request_response.request.header:
            request_object['headers'][header_object.key] = header_object.value
    return request_object

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
