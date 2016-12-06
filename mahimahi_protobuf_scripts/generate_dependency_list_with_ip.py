from argparse import ArgumentParser

import http_record_pb2

import common_module
import os

def main(record_dir, dependency_dir, page_to_time_mapping, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    page_to_time_mapping = common_module.get_page_to_time_mapping(page_to_time_mapping)
    pages = os.listdir(dependency_dir)
    for page in pages:
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if page not in page_to_time_mapping:
            continue
        record_directory = os.path.join(record_dir, page_to_time_mapping[page], page)
        dependencies, dependency_lines = get_dependencies(dependency_filename)
        dependency_to_ip = get_dependency_to_ip(dependencies, record_directory)
        output_to_file(dependency_lines, dependency_to_ip, output_dir, page)

def output_to_file(dependency_lines, dependency_to_ip, output_dir, page):
    page_output_dir = os.path.join(output_dir, page)
    if not os.path.exists(page_output_dir):
        os.mkdir(page_output_dir)
    output_filename = os.path.join(output_dir, page, 'dependency_tree.txt')
    with open(output_filename, 'wb') as output_file:
        for raw_line in dependency_lines:
            line = raw_line.strip().split()
            url = line[2]
            if url in dependency_to_ip:
                ip = dependency_to_ip[url]
                raw_line += ' ' + str(ip)
                output_file.write(raw_line + '\n')

def get_dependency_to_ip(dependencies, record_directory):
    result = dict()
    files = os.listdir(record_directory)
    for f in files:
        url, ip = get_url_and_ip(os.path.join(record_directory, f))
        if url in dependencies:
            print '{0} {1}'.format(url, ip)
            result[url] = ip
    return result

def get_url_and_ip(filename):
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line
        splitted_first_line = first_line.split()
        response_object = request_response.response
        url = splitted_first_line[1]
        hostname = get_hostname(request_response)
        full_url = 'http://' if request_response.scheme == 1 else 'https://'
        full_url += hostname + url
        return full_url, request_response.ip

def get_hostname(request_response):
    for header_object in request_response.request.header:
        if header_object.key == 'Host':
            return header_object.value

def get_dependencies(dependency_filename):
    dependency_list = set()
    dependency_lines = []
    with open(dependency_filename, 'rb') as input_file:
        for i, raw_line in enumerate(input_file):
            line = raw_line.strip().split()
            url = line[2]
            dependency_list.add(url)
            dependency_lines.append(raw_line.strip())
    return dependency_list, dependency_lines

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('record_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('page_to_time_mapping')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.record_dir, args.dependency_dir, args.page_to_time_mapping, args.output_dir)
