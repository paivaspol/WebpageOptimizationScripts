from argparse import ArgumentParser

import http_record_pb2
import json
import os

def Main():
    ha_requests_urls = GetRequestsUrls(args.requests_filename)
    mm_record_urls = GetMMRecordUrls(args.mm_record_dir)
    missing_records = ha_requests_urls - mm_record_urls
    print('\n'.join(missing_records))

def GetRequestsUrls(requests_filename):
    urls = set()
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            urls.add(entry['url'])
    return urls

def GetMMRecordUrls(mm_record_dir):
    recorded_urls = set()
    for f in os.listdir(mm_record_dir):
        filename = os.path.join(mm_record_dir, f)
        with open(filename, 'rb') as input_file:
            file_content = input_file.read()
            request_response = http_record_pb2.RequestResponse()
            request_response.ParseFromString(file_content)
            url = ConstructUrlFromMahimahiRecord(request_response)
            recorded_urls.add(url)
    return recorded_urls

def ConstructUrlFromMahimahiRecord(mahimahi_record):
    '''Returns the URL of the recorded file.'''
    first_line = mahimahi_record.request.first_line
    splitted_first_line = first_line.split()
    host = b''
    for header_pair in mahimahi_record.request.header:
        if header_pair.key == b'Host':
            host = header_pair.value
    scheme = 'http://' if mahimahi_record.scheme == http_record_pb2.RequestResponse.HTTP else 'https://'
    return scheme + host.decode('utf-8') + splitted_first_line[1].decode('utf-8')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    parser.add_argument('mm_record_dir')
    args = parser.parse_args()
    Main()
