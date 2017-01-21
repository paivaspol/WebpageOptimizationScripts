from argparse import ArgumentParser
from shutil import copyfile

import http_record_pb2

import common_module
import os

def main(record_dir):
    files = os.listdir(record_dir)
    for f in files:
        full_path = os.path.join(record_dir, f)
        url, ip = get_url_and_ip(full_path)
        print url + ' ' + ip
        if 'http://' in url or 'https://' in url:
            copied_filename = copy_file(full_path)
            remove_slash(copied_filename)

def remove_slash(filename):
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line
        splitted_first_line = first_line.split()
        if 'http://' in splitted_first_line[1]:
            print 'here'
            splitted_first_line[1] = splitted_first_line[1].replace('http://', 'http:/')
        if 'https://' in splitted_first_line[1]:
            print 'here (1)'
            splitted_first_line[1] = splitted_first_line[1].replace('https://', 'https:/')
        request_response.request.first_line = splitted_first_line[0] + ' ' + \
                                              splitted_first_line[1] + ' ' + \
                                              splitted_first_line[2]
        print request_response.request.first_line
    with open(filename, 'wb') as output_file:
        output_file.write(request_response.SerializeToString())

def copy_file(src):
    dst = src + '.removed_slash'
    copyfile(src, dst)
    return dst

def get_url_and_ip(filename):
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line
        splitted_first_line = first_line.split()
        response_object = request_response.response
        url = splitted_first_line[1]
        full_url = url
        return full_url, request_response.ip

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('record_dir')
    args = parser.parse_args()
    main(args.record_dir)
