from argparse import ArgumentParser

import json
import os

def Main():
    for d in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        total_bytes, total_count = GetBytesAndCount(network_filename)
        print('{0} {1} {2}'.format(d, total_count, total_bytes))


def GetBytesAndCount(network_filename):
    with open(network_filename, 'r') as input_file:
        req_ids = set()
        total_bytes = 0
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                req_ids.add(req_id)
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    continue
                size = int(e['params']['encodedDataLength'])
                total_bytes += size
        return total_bytes, len(req_ids)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
