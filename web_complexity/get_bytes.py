from argparse import ArgumentParser
from collections import defaultdict

import os
import json

def Main():
    for d in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        if not os.path.exists(network_filename):
            continue
        with open(network_filename, 'r') as input_file:
            # req_id_to_bytes = defaultdict()
            total_bytes = 0
            # resources = set()
            resources = []
            request_id_to_url = {}
            req_ids_to_ignore = set()
            for l in input_file:
                e = json.loads(l.strip())
                if e['method'] == 'Network.requestWillBeSent':
                    url = e['params']['request']['url']
                    request_id = e['params']['requestId']
                    request_id_to_url[request_id] = url
                    if not url.startswith('http'):
                        req_ids_to_ignore.add(request_id)
                if e['method'] == 'Network.loadingFinished':
                    request_id = e['params']['requestId']
                    if request_id in req_ids_to_ignore or request_id not in request_id_to_url:
                        continue
                    # req_id_to_bytes[e['params']['requestId']] = e['encodedDataLength']
                    # if request_id not in request_id_to_url:
                    #     continue

                    url = request_id_to_url[request_id]
                    # if url in resources:
                    #     continue

                    total_bytes += e['params']['encodedDataLength']
                    # resources.add(url)
                    resources.append(url)
            if total_bytes > 0:
                print('{0} {1} {2}'.format(d, total_bytes, len(resources)))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
