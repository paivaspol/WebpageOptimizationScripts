from argparse import ArgumentParser

import http_record_pb2

import os

def main(record_directory):
    files = os.listdir(record_directory)
    for f in files:
        full_path = os.path.join(record_directory, f)
        get_filename(full_path)

def get_filename(filename):
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line
        ip = '[NONE]' if len(request_response.ip) == 0 else request_response.ip
        port = request_response.port
        splitted_first_line = first_line.split()
        print first_line + ' ' + ip + ' ' + str(port)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('record_directory')
    args = parser.parse_args()
    main(args.record_directory)
