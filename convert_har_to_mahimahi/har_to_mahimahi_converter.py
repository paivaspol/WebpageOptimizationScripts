import http_record_pb2

from argparse import ArgumentParser
from urlparse import urlparse

import os
import simplejson as json

DELIMETER = '\r\n'

def process_har_file(har_file, output_dir):
    har_obj = json.load(open(har_file))
    entries = har_obj['log']['entries']
    for obj_id, entry in enumerate(entries):
        request_response = http_record_pb2.RequestResponse()
        # Note: IP and Port cannot be retrieved from HAR file.
        # Since everything is already recorded, just use HTTP instead of HTTPS
        request_response.scheme = 1

        entry_request = entry['request']
        request = http_record_pb2.HTTPMessage()
        first_line = '{0} {1} {2}'.format(entry_request['method'], \
                                          entry_request['url'], \
                                          entry_request['httpVersion'])
        request.first_line = first_line
        for request_header in entry_request['headers']:
            header = request.header.add()
            header.key = request_header['name']
            header.value = request_header['value']
        request_response.request.CopyFrom(request)

        entry_response = entry['response']
        response = http_record_pb2.HTTPMessage()
        first_line = '{0} {1} {2}'.format(entry_response['httpVersion'], \
                                          entry_response['status'], \
                                          entry_response['statusText'])
        response.first_line = first_line
        for response_header in entry_response['headers']:
            header = response.header.add()
            header.key = response_header['name']
            header.value = response_header['value']
        if 'text' in entry_response['content']:
            response.body = entry_response['content']['text'].encode('utf-8')
        request_response.response.CopyFrom(response)
        url = entry_request['url']
        write_to_file(output_dir, request_response, obj_id)

def write_to_file(output_dir, request_response_obj, obj_id):
    with open(os.path.join(output_dir, str(obj_id)), 'wb') as output_file:
        output_file.write(request_response_obj.SerializeToString())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('har_file')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    process_har_file(args.har_file, args.output_dir)
