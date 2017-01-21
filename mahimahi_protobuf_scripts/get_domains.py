from argparse import ArgumentParser

import http_record_pb2

import os

def main(record_directory, page_to_timestamp_filename, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    page_to_timestamp = get_page_to_timestamp(page_to_timestamp_filename)
    for page, timestamp in page_to_timestamp.iteritems():
        page_record_dir = os.path.join(record_directory, timestamp, page)
        if not os.path.exists(page_record_dir):
            continue
        files = os.listdir(page_record_dir)
        hostnames = set()
        for f in files:
            full_path = os.path.join(page_record_dir, f)
            hostnames.add(get_hostname(full_path))
        output_to_file(output_dir, page, hostnames)


def output_to_file(output_dir, page, hostnames):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for hostname in hostnames:
            output_file.write('{0}\n'.format(hostname))

def get_hostname(record_filename):
    with open(record_filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        response_object = request_response.response
        for header in request_response.request.header:
            if header.key == 'Host':
                return header.value

def get_page_to_timestamp(page_to_timestamp_filename):
    result = dict()
    with open(page_to_timestamp_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = line[1]
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('record_directory')
    parser.add_argument('page_to_timestamp')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.record_directory, args.page_to_timestamp, args.output_dir)
