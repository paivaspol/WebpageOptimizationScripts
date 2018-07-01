'''
Finds the cache times of the intersected resources.
'''
from argparse import ArgumentParser
from collections import defaultdict

import os
import json
import math

def Main():
    landing_page_urls, cache_times = GetUrlsAndCacheTimes(args.landing_page_crawl)
    outgoing_links_urls_histogram = defaultdict(int)
    total_pages = 0
    for d in os.listdir(args.outgoing_links_crawl):
        network_filename = os.path.join(args.outgoing_links_crawl, d, 'network_' + d)
        if not os.path.exists(network_filename):
            continue
        urls, _ = GetUrlsAndCacheTimes(network_filename)
        for url in urls:
            outgoing_links_urls_histogram[url] += 1
        total_pages += 1

    outgoing_links_urls = GetUrlsToConsider(outgoing_links_urls_histogram, \
                                            total_pages, \
                                            args.percent_consider)
    intersection = landing_page_urls & outgoing_links_urls
    for url in intersection:
        if url not in cache_times:
            continue
        print('{0} {1}'.format(url, cache_times[url]))


def GetUrlsToConsider(urls_histogram, total_pages, percent_consider):
    '''
    Returns a set of urls to be considering.
    '''
    num_considering = int(math.ceil(percent_consider / 100.0 * total_pages))
    urls_considered = set()
    for url, count in urls_histogram.items():
        if count < num_considering:
            continue
        urls_considered.add(url)
    return urls_considered


def GetUrlsAndCacheTimes(network_filename):
    urls = set()
    cache_time = {}
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue
                urls.add(url)
            elif e['method'] == 'Network.responseReceived':
                url = e['params']['response']['url']
                if not url.startswith('http'):
                    continue
                cache_time[url] = ParseCacheTime(e['params']['response']['headers'])
    return urls, cache_time


def ParseCacheTime(headers):
    '''
    Returns the cache time, in seconds.
    '''
    if 'cache-control' not in headers:
        return 0
    cache_value = headers['cache-control'].split('=')
    for i, v in enumerate(cache_value):
        if v == 'max-age':
            return cache_value[i + 1]
    return 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('landing_page_crawl')
    parser.add_argument('outgoing_links_crawl')
    parser.add_argument('percent_consider', type=int)
    args = parser.parse_args()
    Main()
