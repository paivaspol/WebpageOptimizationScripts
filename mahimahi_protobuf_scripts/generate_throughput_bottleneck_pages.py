from argparse import ArgumentParser

import http_record_pb2

import common_module
import os

HOST = 'http://test.com'

def main(page_resource_sizes_directory, record_template_directory, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    main_html, resource_template = get_template_objects(record_template_directory)
    pages = os.listdir(page_resource_sizes_directory)
    for page in pages:
        print HOST + '/' + page
        resource_sizes_filename = os.path.join(page_resource_sizes_directory, page)
        page_output_dir = os.path.join(output_dir, page)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)
        request_ids = generate_pages_from_template(resource_sizes_filename, resource_template, page_output_dir, page)
        generate_new_main_html(main_html, request_ids, page_output_dir, page)

def generate_new_main_html(main_html_request_response_template, request_ids, page_output_dir, page):
    # We have to do some modifications to the request response object.
    #   1. Modify the first line in the request
    #   2. Modify the body of the response.
    #   3. Modify the content-length in the response HTTP header.
    main_html_request_response = http_record_pb2.RequestResponse()
    main_html_request_response.CopyFrom(main_html_request_response_template)

    # Modify the first line. Use the request id as the resource name.
    template_first_line = main_html_request_response.request.first_line.strip().split()
    first_line = template_first_line[0] + ' /' + page + '/ ' + template_first_line[2]
    main_html_request_response.request.first_line = first_line

    # Modify the HTML body
    html_body = generate_html_body(request_ids)
    main_html_request_response.response.body = html_body
    
    # Modify the content length
    modify_http_header(main_html_request_response.response.header, 'content-length', str(len(html_body)))

    # Modify the request URL
    modify_http_header(main_html_request_response.request.header, 'host', HOST)

    output_to_file(main_html_request_response, page_output_dir, 'index')

def generate_html_body(request_ids):
    body = '<html><head></head><body>'
    for request_id in request_ids:
        body += '<iframe src="' + request_id + '"></iframe>'
    body += '</body></html>'
    return body

def generate_pages_from_template(resource_size_mapping_filename, resource_template, output_dir, page):
    request_ids = []
    with open(resource_size_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if line[2].startswith('data'):
                continue
            request_id, size, url = line
            resource_request_response = http_record_pb2.RequestResponse()
            resource_request_response.CopyFrom(resource_template)

            # We have to do some modifications to the request response object.
            #   1. Modify the first line in the request
            #   2. Modify the body of the response.
            #   3. Modify the content-length in the response HTTP header.
            #   4. Modify the host of the page.

            # Modify the first line. Use the request id as the resource name.
            template_first_line = resource_request_response.request.first_line.strip().split()
            first_line = template_first_line[0] + ' /' + page + '/' + request_id + ' ' + template_first_line[2]
            resource_request_response.request.first_line = first_line

            # Modify the body of the response. Get a string with that amount of bytes.
            response_body = generate_response_body(size)
            resource_request_response.response.body = response_body

            # Modify the content length
            modify_http_header(resource_request_response.response.header, 'content-length', size)

            # Modify the request URL
            modify_http_header(resource_request_response.request.header, 'host', HOST)

            request_ids.append(request_id)
            output_to_file(resource_request_response, output_dir, request_id)
    return request_ids

def output_to_file(resource_request_response, output_dir, filename):
    file_content = resource_request_response.SerializeToString()
    output_filename = os.path.join(output_dir, filename)
    with open(output_filename, 'wb') as output_file:
        output_file.write(file_content)

def modify_http_header(http_headers, header_key, header_value):
    for http_header in http_headers:
        if header_key.lower() == http_header.key.lower():
            http_header.value = header_value
            break

def generate_response_body(num_bytes):
    result = ''
    for i in range(0, int(num_bytes)):
        result += '@'
    return result

def get_template_objects(record_template_directory):
    files = os.listdir(record_template_directory)
    placeholder_request_response = None
    main_html_request_response = None
    for recorded_file in files:
        path = os.path.join(record_template_directory, recorded_file)
        with open(path, 'rb') as input_file:
            file_content = input_file.read()
            request_response = http_record_pb2.RequestResponse()
            request_response.ParseFromString(file_content)
            if 'placeholder.html' in request_response.request.first_line:
                placeholder_request_response = request_response
            elif request_response.request.first_line.strip().split()[1].endswith('throughput_bottleneck/'):
                main_html_request_response = request_response
    return main_html_request_response, placeholder_request_response

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_resource_sizes_directory')
    parser.add_argument('record_template_directory')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.page_resource_sizes_directory, args.record_template_directory, args.output_dir)
