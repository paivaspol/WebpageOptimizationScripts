from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import json
import os

def Main():
    histogram = defaultdict(int)
    for p in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        urls = GetURLs(network_filename)
        for u in urls:
            histogram[u] += 1
    sorted_histogram = sorted(histogram.iteritems(), key=lambda x: x[1], reverse=True)
    counter = 0
    for k, v in sorted_histogram:
        parsed_url = urlparse(k)
        color = 1 
        if args.main_domain in parsed_url.netloc and (parsed_url.path.endswith('.js') or parsed_url.path.endswith('.css')):
            color = 3
        elif args.main_domain in parsed_url.netloc:
            color = 4
        print '{0} {1} {2} {3}'.format(k, counter, v, color)
        counter += 1


def GetURLs(network_filename):
    urls = set()
    found_first_request = False
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                if not found_first_request:
                    found_first_request = True
                    continue

                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue 
                urls.add(url)
    return urls
 

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('main_domain')
    args = parser.parse_args()
    Main()
