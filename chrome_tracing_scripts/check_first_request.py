from argparse import ArgumentParser

import common_module
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
DOCUMENT_URL = 'documentURL'
REDIRECT_RESPONSE = 'redirectResponse'
RESPONSE = 'response'
URL = 'url'

def check_requests(url, network_events_filename):
    with open(network_events_filename, 'rb') as input_file:
        first_event = json.loads(json.loads(input_file.readline().strip()))
        original_url = None
        if PARAMS in first_event and DOCUMENT_URL in first_event[PARAMS]:
            original_url = first_event[PARAMS][DOCUMENT_URL]

        while first_event[METHOD] != 'Network.requestWillBeSent' or \
            (DOCUMENT_URL in first_event[PARAMS] and \
            url not in first_event[PARAMS][DOCUMENT_URL]):
            first_event = json.loads(json.loads(input_file.readline().strip()))
            if PARAMS in first_event and DOCUMENT_URL in first_event[PARAMS]:
                original_url = first_event[PARAMS][DOCUMENT_URL]

        second_event = json.loads(json.loads(input_file.readline().strip()))
        final_url = None
        if PARAMS in second_event and \
            RESPONSE in second_event[PARAMS] and \
            URL in second_event[PARAMS][RESPONSE]:
            final_url = second_event[PARAMS][RESPONSE][URL]
        while second_event[METHOD] != 'Network.responseReceived' or \
            (DOCUMENT_URL in second_event[PARAMS] and \
            url not in second_event[PARAMS][RESPONSE]['url']):
                second_event = json.loads(json.loads(input_file.readline().strip()))
                if PARAMS in second_event and \
                    RESPONSE in second_event[PARAMS] and \
                    URL in second_event[PARAMS][RESPONSE]:
                    final_url = second_event[PARAMS][RESPONSE][URL]
        print original_url + ' ' + final_url

def traverse_directories(root_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        network_filename = os.path.join(path, 'network_' + url)
        check_requests(url, network_filename)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    traverse_directories(args.root_dir)
