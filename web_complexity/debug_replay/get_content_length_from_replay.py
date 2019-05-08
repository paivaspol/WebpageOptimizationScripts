from argparse import ArgumentParser

import json
import os

def Main():
    for d in os.listdir(args.root_dir):
        if 'sanook' not in d:
            continue
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        ProcessNetworkFile(network_filename)

def ProcessNetworkFile(network_filename):
    with open(network_filename, 'r') as input_file:
        req_id_to_type = {}
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                req_id = e['params']['requestId']
                req_type = e['params']['type']
                req_id_to_type[req_id] = req_type
            elif e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                url = e['params']['response']['url']
                if not url.startswith('http'):
                    continue
                content_length = GetContentLength(e)
                content_type = req_id_to_type[req_id] if req_id in req_id_to_type else '[MISSING_CONTENT_TYPE'
                print('{0} {1} {2}'.format(url, content_length, content_type))
                found_response = True


def GetContentLength(entry):
    '''Returns the content-length of the response.'''
    headers = entry['params']['response']['headers']
    for k, v in headers.items():
        if k.lower() == 'content-length':
            return v
    return -1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
