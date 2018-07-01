'''
Analysis description:
To prefetch during the user-think time, it is important to know the amount of 
time needed to prefetch resources.

This script produces the time it takes to prefetch different number of 
resources with a particular network configuration e.g. 3G, 4G. Further,
it assumes that the resources that should be prefetched are included based on
how common the resource is across outgoing links.
'''
from argparse import ArgumentParser
from collections import defaultdict
from urllib.parse import urlparse

import common_module
import os
import sys

# Network configuration based on https://github.com/WPO-Foundation/webpagetest/blob/master/www/settings/connectivity.ini.sample
NETWORK_PARAMS = {
    '3G': 1600000,
    '4G': 9000000,
    'LTE': 12000000,
}

def Main():
    histogram, resource_sizes = \
            GenerateResourceHistogramAndResourceSizeAcrossPages(args.root_dir)
    sorted_histogram = sorted(histogram.items(), \
            key=lambda x: (x[1], x[0]), \
            reverse=True)
    # print(sorted_histogram[:10])
    # print(resource_sizes)
    count = 0
    cumulative_resource_size = 0
    for resource_url, freq in sorted_histogram:
        if resource_url not in resource_sizes:
            continue

        # Exceeds threshold.
        if count > args.resource_limit:
            break

        resource_size = resource_sizes[resource_url]
        cumulative_resource_size += resource_size
        network_params_bps = NETWORK_PARAMS[args.network_config]
        fetch_time = ComputeFetchTime(cumulative_resource_size, network_params_bps)
        count += 1
        print('{0} {1} {2}'.format(count, fetch_time, cumulative_resource_size))


def ComputeFetchTime(resource_size, download_bandwidth):
    '''
    Return the time, in seconds, to use the fetch the amount of bytes

    Params:
      - resource_size bytes
      - download_bandwidth bps
    '''
    return resource_size * 8 / download_bandwidth


def GenerateResourceHistogramAndResourceSizeAcrossPages(crawl_dir):
    '''
    Generates a histogram and resource sizes of the resources appearing all 
    pages in the crawl.
    '''
    histogram = defaultdict(int)
    resource_sizes = defaultdict(int)
    for p in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        urls, page_resource_sizes = GetURLsAndResourceSize(network_filename)
        for u in urls:
            histogram[u] += 1

        for resource, size in page_resource_sizes.items():
            resource_sizes[resource] = max(resource_sizes[resource], size)
    return histogram, resource_sizes


def GetURLsAndResourceSize(network_filename):
    '''
    Returns a set containing the URLs of the requests.
    '''
    import json
    urls = set()
    found_first_request = False

    request_id_url = {}
    resource_sizes = {}
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                if not found_first_request:
                    found_first_request = True
                    continue

                request_id = e['params']['requestId']
                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue 
                request_id_url[request_id] = url
                urls.add(url)
            elif e['method'] == 'Network.loadingFinished':
                request_id = e['params']['requestId']
                if not request_id in request_id_url:
                    continue

                url = request_id_url[request_id]
                response_size = e['params']['encodedDataLength']
                resource_sizes[url] = response_size
    return urls, resource_sizes


if __name__ == '__main__':
    parser = ArgumentParser(description='This script produces the time it takes\
            to prefetch different number of resources with a particular network\
            configuration e.g. 3G, 4G. Further, it assumes that the resources \
            that should be prefetched are included based on how common the \
            resource is across outgoing links.')
    parser.add_argument('root_dir', \
            help='The root directory that  contains the crawl data')
    parser.add_argument('network_config', \
            choices=list(NETWORK_PARAMS.keys()), \
            help='The network config used to calculate the time to fetch the \
            resources')
    parser.add_argument('--resource-limit', \
                        type=int, \
                        help='The max number of resource to consider', \
                        default=sys.maxsize)
    args = parser.parse_args()
    Main()
