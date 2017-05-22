from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import json
import os

def main(domains, root_dir):
    for p in os.listdir(root_dir):
        # if 'm.accuweather.com' not in p:
        #     continue
        network_filename = os.path.join(root_dir, p, 'network_' + p)
        page_domains = domains[p]
        urls = get_urls(network_filename, p)
        first_party_count = 0
        for url in urls:
            domain = urlparse(url).netloc
            if domain in page_domains:
                first_party_count += 1
                # print url
        fraction = 1.0 * first_party_count / len(urls)
        if fraction > 0:
            print '{0} {1} {2} {3}'.format(p, first_party_count, len(urls), fraction)


def get_urls(network_filename, p):
    urls = []
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for l in input_file:
            network_event = json.loads(l.strip())
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                if not found_first_request:
                    if common_module.escape_page(url) == p:
                        found_first_request = True
            elif found_first_request and network_event['method'] == 'Network.responseReceived':
                url = network_event['params']['response']['url']
                if not url.startswith('data:'):
                    urls.append(url)
    return urls

def get_domains(domains_dir):
    result = defaultdict(set)
    for p in os.listdir(domains_dir):
        input_filename = os.path.join(domains_dir, p)
        with open(input_filename, 'rb') as input_file:
            for d in input_file:
                result[p].add(d.strip())
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('domains_dir')
    args = parser.parse_args()
    domains = get_domains(args.domains_dir)
    main(domains, args.root_dir)
