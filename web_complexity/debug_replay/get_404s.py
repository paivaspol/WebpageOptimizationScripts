from argparse import ArgumentParser

import json
import os

def Main():
    for d in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        cnt, total = Get404Count(network_filename)
        frac = 1.0 * cnt / total
        print('{0} {1} {2}'.format(d, cnt, frac))


def Get404Count(network_filename):
    '''Returns the count of number of resources that got response of 404.'''
    with open(network_filename, 'r') as input_file:
        count = 0
        req_ids = set()
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.responseReceived':
                req_ids.add(e['params']['requestId'])
                if e['params']['response']['status'] == 404:
                    count += 1
        return count, len(req_ids)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
