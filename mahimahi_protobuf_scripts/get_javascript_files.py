from argparse import ArgumentParser
from urlparse import urlparse

import http_record_pb2

import common_module
import os
import zlib

def main(root_dir, output_dir, page_list, page_to_time_mapping):
    for page in page_list:
        print page
        page = common_module.escape_page(page)
        timestamp = page_to_time_mapping[page]
        page_directory = os.path.join(root_dir, timestamp, page)
        file_list = os.listdir(page_directory)
        page_output_dir = os.path.join(output_dir, page)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)

        counter = 0
        counter_to_url_mapping_filename = os.path.join(page_output_dir, 'filename_url_map.txt')
        with open(counter_to_url_mapping_filename, 'wb') as output_file:
            for filename in file_list:
                record_filename = os.path.join(page_directory, filename)
                # Only get the response if the URL is a javascript URL.
                try:
                    url, response_body = get_response(record_filename)
                    parsed_url = urlparse(url)
                    if parsed_url.path.endswith('.js'):
                        output_filename = os.path.join(page_output_dir, str(counter))
                        write_response_to_file(output_filename, response_body)
                        output_file.write('{0} {1}\n'.format(counter, url))
                        counter += 1
                except Exception as e:
                    pass
                        

def write_response_to_file(filename, response_body):
    with open(filename, 'wb') as output_file:
        output_file.write(response_body.encode('utf-8'))

def get_response(record_filename):
    with open(record_filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        response_object = request_response.response
        url = request_response.request.first_line.split()[1]
        # print url
        # print request_response.response.header
        use_gzip = False
        for header in request_response.response.header:
            if header.key == 'Content-Encoding':
                print header.value
                use_gzip = True

        if use_gzip:
            return url, zlib.decompress(response_object.body).decode('utf-8')
        else:
            return url, response_object.body

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
