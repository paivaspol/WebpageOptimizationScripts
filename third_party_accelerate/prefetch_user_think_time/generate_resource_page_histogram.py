from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import json
import os

def Main():
    histogram = defaultdict(int)
    for p in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        urls = common_module.GetURLs(network_filename)
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


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('main_domain')
    args = parser.parse_args()
    Main()
