from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import json
import os

def Main():
    histogram = defaultdict(int)
    page_count = 0
    base_page = common_module.GetBasePage(args.root_dir)
    all_pages = os.listdir(args.root_dir)
    if args.group_pages:
        all_pages = common_module.GetUrlsWithMostCommonPrefix(all_pages)
    for p in all_pages:
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        page_count += 1
        urls, first_request = common_module.GetURLs(network_filename)

        # This is just the same page...
        if first_request is None or \
            base_page == common_module.EscapeURL(first_request):
            continue
            
        for u in urls:
            histogram[u] += 1
    sorted_histogram = sorted(histogram.items(), key=lambda x: x[1], reverse=True)
    resource_id = 0
    for k, v in sorted_histogram:
        parsed_url = urlparse(k)
        color = 1 
        if args.main_domain in parsed_url.netloc and (parsed_url.path.endswith('.js') or parsed_url.path.endswith('.css')):
            color = 3
        elif args.main_domain in parsed_url.netloc:
            color = 4
        print('{0} {1} {2} {3} {4}'.format(k, resource_id, v, color, page_count))
        resource_id += 1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--main-domain', default='[NONE_EXISTENT_RESOURCE]')
    parser.add_argument('--group-pages', \
            help='Whether to group pages on some common prefix', \
            default=False, action='store_true')
    args = parser.parse_args()
    Main()
