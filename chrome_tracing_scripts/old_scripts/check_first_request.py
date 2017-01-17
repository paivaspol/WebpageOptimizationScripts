from argparse import ArgumentParser

import common_module
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
DOCUMENT_URL = 'documentURL'
REDIRECT_RESPONSE = 'redirectResponse'
REQUEST = 'request'
RESPONSE = 'response'
URL = 'url'

def check_requests(url, network_events_filename):
    with open(network_events_filename, 'rb') as input_file:
        original_url = None
        try:
            line = input_file.readline()
            while line != '':
                first_event = json.loads(json.loads(line.strip()))
                if first_event[METHOD] == 'Network.requestWillBeSent' or \
                    (REQUEST in first_event[PARAMS] and \
                    common_module.escape_page(url) in \
                        common_module.escape_page(first_event[PARAMS][REQUEST][URL])):
                    if PARAMS in first_event and REQUEST in first_event[PARAMS]:
                        original_url = first_event[PARAMS][REQUEST][URL]
                        if original_url is not None:
                            break
                line = input_file.readline()

            final_url = None
            line = input_file.readline()
            while line != '':
                second_event = json.loads(json.loads(line.strip()))
                if second_event[METHOD] == 'Network.responseReceived' and \
                    PARAMS in second_event and \
                    RESPONSE in second_event[PARAMS] and \
                    URL in second_event[PARAMS][RESPONSE]:
                    final_url = second_event[PARAMS][RESPONSE][URL]
                    if final_url is not None:
                        break
                line = input_file.readline()
            if final_url is None:
                print original_url + ' ' + original_url
            else:
                print original_url + ' ' + final_url

        except json.scanner.JSONDecodeError as e:
            print 'error: ' + url
            pass

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
