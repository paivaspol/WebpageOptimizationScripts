from argparse import ArgumentParser

import json
import os

def Main():
    total = 0
    failed = 0
    for d in os.listdir(args.root_dir):
        total += 1
        net_filename = os.path.join(args.root_dir, d, 'network_' + d)
        if not os.path.exists(net_filename):
            print(d)
            failed += 1
            continue

        req_count = GetResourceCount(net_filename)
        if req_count == 1:
            failed += 1
            print('{0}'.format(d))
    print('failed: {0} total: {1}'.format(failed, total))


def GetResourceCount(network_filename):
    req_ids = set()
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                req_ids.add(e['params']['requestId'])
    return len(req_ids)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
