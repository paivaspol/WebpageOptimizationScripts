from argparse import ArgumentParser

import json
import os

def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    
    page_count = sum([ 1 for p in os.listdir(args.root_dir) ])

    for i, p in enumerate(os.listdir(args.root_dir)):
        print '{0}/{1} Completed...'.format(i, page_count)
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        requests = GetRequests(network_filename)
        OutputToFile(p, requests)


def OutputToFile(p, requests):
    output_file = os.path.join(args.output_dir, p)
    with open(output_file, 'w') as output_file:
        for r in requests:
            output_file.write(r + '\n')


def GetRequests(network_filename):
    requests = []
    seen = set()
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                if url in seen or url.startswith('data'):
                    # Skip duplicated URLs and data URLs.
                    continue
                requests.append(url)
                seen.add(url)
    return requests


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
