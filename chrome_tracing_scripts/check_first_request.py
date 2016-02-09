from argparse import ArgumentParser

import common_module
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
DOCUMENT_URL = 'documentURL'
REDIRECT_RESPONSE = 'redirectResponse'

def check_requests(network_events_filename):
    with open(network_events_filename, 'rb') as input_file:
        first_event = json.loads(json.loads(input_file.readline().strip()))
        while first_event[METHOD] != 'Network.requestWillBeSent':
            first_event = json.loads(json.loads(input_file.readline().strip()))
        second_event = json.loads(json.loads(input_file.readline().strip()))
        if first_event[PARAMS][REQUEST_ID] == second_event[PARAMS][REQUEST_ID] and \
            DOCUMENT_URL in first_event[PARAMS] and \
            DOCUMENT_URL in second_event[PARAMS] and \
            REDIRECT_RESPONSE in second_event[PARAMS]:
            redirected_url = second_event[PARAMS][DOCUMENT_URL]
            print first_event[PARAMS][DOCUMENT_URL] + ' ' + second_event[PARAMS][DOCUMENT_URL]
        else:
            print first_event[PARAMS][DOCUMENT_URL]

def traverse_directories(root_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        network_filename = os.path.join(path, 'network_' + url)
        check_requests(network_filename)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    traverse_directories(args.root_dir)
